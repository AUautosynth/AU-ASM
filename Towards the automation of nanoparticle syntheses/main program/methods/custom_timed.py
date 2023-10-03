from GUI_functions.method_functions import start_sequence, end_sequence
from settings import settings

experiment_data = settings.experiment_data
pump_objects = settings.pump_objects
experiment_data = experiment_data.reset_index(drop=True)

# Standard import
import sys
import time
import pandas as pd

# Local import
from GUI_functions.method_functions import move_to

gantt_timer_dictionary = {}


# Used to calculate the time taken for the next dosage
def time_calculator(volume_temporary, pump, x=settings.X, y=settings.Y):
    timed_calculation = move_to(x, y, time_calculation=True)
    timed_calculation += pump.dose(volume_temporary, time_calculation=True)

    return timed_calculation


start = time.time()
# The first step is to sort the data and order it.

# Isolate the prioritization dataframe
prioritization_df = experiment_data.loc[:, "Priority Solution 1":]
prioritization_df.pop("x-coordinate")
prioritization_df.pop("y-coordinate")

# Slice the prioritization dataframe into two, a prio and a timer dataframe
temporary_integer_for_slicing = int((len(prioritization_df.columns) + 1) / 2)
timer_df = prioritization_df.iloc[:, temporary_integer_for_slicing:]
prio_df = prioritization_df.iloc[:, :temporary_integer_for_slicing]

# The dosing dictionary has priority dictionaries in it, so that it dose in the wanted order.
dosing_data_dictionary = {}
number_of_prioritizations = len(prio_df.columns)
for i in range(number_of_prioritizations):
    dosing_data_dictionary['Priority {}'.format(i + 1)] = {}

# Iterate over the rows and store the experimentinformation correctly according to prioritization
first_iteration = True
for prio_key in dosing_data_dictionary:

    if first_iteration:

        for experiment_number, row in prio_df.iterrows():
            # The try statement handles an error which occurs when the user forgets to do the prioritisation correctly
            # there should always be atleast a priority 1, so the program should stop
            try:
                solution_number = row[row == float(prio_key[-1])].index[0][-1]
                volume = experiment_data.loc[experiment_number, 'Solution {}'.format(solution_number)]
                if volume == 0:
                    continue
                x = experiment_data.loc[experiment_number, "x-coordinate"]
                y = experiment_data.loc[experiment_number, "y-coordinate"]

                dosing_data_dictionary[prio_key][experiment_number] = {"Solvent": int(solution_number),
                                                                       "Volume": volume
                    , "x": x, "y": y}

            except Exception:
                print("ERROR IN PRIORITIZATION SHEET")
                sys.exit()
        first_iteration = False
    else:

        for experiment_number, row in prio_df.iterrows():

            # The try statement handles if there is not a priority that high for the current vial. It is expected that not all vials should have the same amount of solutions in them
            # therefore just skip it, which is also why the except statement only has a pass
            # There is the possibility of handling the above error as if the error is an intentional feature, needs to be fixed
            # It needs to check if the error is a "There is no such prioritization for that vial" or "There is a duplicate"
            try:

                solution_number = row[row == float(prio_key[-1])].index[0][-1]
                volume = experiment_data.loc[experiment_number, "Solution {}".format(solution_number)]
                if volume == 0:
                    continue
                x = experiment_data.loc[experiment_number, "x-coordinate"]
                y = experiment_data.loc[experiment_number, "y-coordinate"]
                timer = timer_df.loc[experiment_number, "Timer Priority " + (prio_key[-1])]

                dosing_data_dictionary[prio_key][experiment_number] = {"Solvent": int(solution_number),
                                                                       "Volume": volume
                    , "x": x, "y": y, "Timer": timer}

            except Exception:
                pass

timed_dosages = {}
# For loop used to iterate through all dosing which has priority 1.
# Also, start a timer for the next priority
start_sequence(prime=pump_objects)
for experiment_key in dosing_data_dictionary['Priority 1']:
    # print(experiment_key)
    # Read the vial information
    volume = dosing_data_dictionary['Priority 1'][experiment_key]['Volume']
    solution_number = dosing_data_dictionary['Priority 1'][experiment_key]['Solvent']
    x = dosing_data_dictionary['Priority 1'][experiment_key]['x']
    y = dosing_data_dictionary['Priority 1'][experiment_key]['y']

    # Check each Timed dosage which has started a timer if it should be dosed instead of the current vial
    while True:
        loop_break_counter = 0
        for dosage in list(timed_dosages):
            timed_dosage_volume = timed_dosages[dosage]['Volume']
            timed_dosage_x = timed_dosages[dosage]['x']
            timed_dosage_y = timed_dosages[dosage]['y']
            timed_dosage_pump_number = timed_dosages[dosage]['Solvent']
            time_current_experiment_takes = time_calculator(volume_temporary=volume,
                                                            pump=pump_objects[solution_number - 1],
                                                            x=x, y=y)

            timer_for_timed_dosage = timed_dosages[dosage]['Timer'] - (
                    time.perf_counter() - timed_dosages[dosage]['Initiated timer'])

            print("Time for this dosage to occur: ", time_current_experiment_takes, " > ",
                  "Time left for next dosage have to happen: ", timer_for_timed_dosage)

            if time_current_experiment_takes > timer_for_timed_dosage:

                # Move to the experiment
                move_to(timed_dosage_x, timed_dosage_y)

                # Wait untill it is time to dose the solution
                try:
                    sleep_time = timed_dosages[dosage]['Timer'] - (
                            time.perf_counter() - timed_dosages[dosage]['Initiated timer'])
                    print("Wait for: ", sleep_time)
                    time.sleep(sleep_time)
                except:
                    pass  # This just makes the code survive a sleep.time with a negative value

                # Dose the timed liquid
                start_experiment_timer = time.time() - start
                pump_objects[timed_dosage_pump_number - 1].dose(timed_dosage_volume)
                duration_timer = time.time() - start - start_experiment_timer
                gantt_timer_dictionary[str(dosage)]["Solution {}".format(timed_dosage_pump_number)] = \
                    {"Dosing initiated": start_experiment_timer, "Dosing duration": duration_timer}

                # Look at the next priority for a dosage into the same vial

                next_dosage_priority = 'Priority {}'.format(int(timed_dosages[dosage]['Priority'] + 1))

                # This takes the current vial row from the Priodf and removes each instance of zero
                temporary_prio_df = pd.DataFrame(prio_df.loc[dosage]).T.loc[:,
                                    (pd.DataFrame(prio_df.loc[dosage]).T != 0).any(axis=0)]

                # This makes it possible to compare the length of that dataframe to the amount of priorties
                # which should be available
                if int(timed_dosages[dosage]['Priority'] + 1) <= len(temporary_prio_df.columns):
                    # Set timer for the next dosage inside the timed dosage dictionary, it inherits
                    # the experiment information for that dosage
                    set_next_timer = dosing_data_dictionary[next_dosage_priority][dosage]['Timer']
                    set_next_volume = dosing_data_dictionary[next_dosage_priority][dosage]['Volume']
                    set_next_solvent = dosing_data_dictionary[next_dosage_priority][dosage]['Solvent']
                    set_next_x = dosing_data_dictionary[next_dosage_priority][dosage]['x']
                    set_next_y = dosing_data_dictionary[next_dosage_priority][dosage]['y']
                    start_timer = time.perf_counter()

                    # This updates the timed dosages experiment entry with new information.
                    timed_dosages[dosage] = {'Initiated timer': start_timer, 'Timer': set_next_timer,
                                             'Volume': set_next_volume, 'Solvent': set_next_solvent,
                                             'Priority': int(next_dosage_priority[-1]),
                                             'x': set_next_x, 'y': set_next_y}
                else:
                    # Remove the experiment entry if there is no more priorities for that experiment
                    del timed_dosages[dosage]
                    # if there is not a counter here, the timed dosage
                    # would be equal to the loop break counter after deleting an entry
                    loop_break_counter += 1
            else:
                loop_break_counter += 1

        # Break out if no timers have been used
        if loop_break_counter == len(timed_dosages):
            break

    # Move to the vial
    move_to(x, y)
    # Dose the liquid
    start_experiment_timer = time.time() - start
    pump_objects[solution_number - 1].dose(volume)
    duration_timer = time.time() - start - start_experiment_timer
    gantt_timer_dictionary[experiment_key]["Solution {}".format(solution_number)] = \
        {"Dosing initiated": start_experiment_timer, "Dosing duration": duration_timer}

    # Set timer for the next dosage inside the timed dosage dictionary, it inherits the data for that dosage
    set_next_timer = dosing_data_dictionary['Priority 2'][experiment_key]['Timer']
    set_next_volume = dosing_data_dictionary['Priority 2'][experiment_key]['Volume']
    set_next_solvent = dosing_data_dictionary['Priority 2'][experiment_key]['Solvent']
    set_next_x = dosing_data_dictionary['Priority 2'][experiment_key]['x']
    set_next_y = dosing_data_dictionary['Priority 2'][experiment_key]['y']
    start_timer = time.perf_counter()

    timed_dosages[experiment_key] = {'Initiated timer': start_timer, 'Timer': set_next_timer,
                                     'Volume': set_next_volume, 'Solvent': set_next_solvent, 'Priority': 2,
                                     'x': set_next_x, 'y': set_next_y}

# After the for-loop every priority 1 has been dosed. This while loop hangs as long as there is vial keys in the timed_dosage dictionary
while True:

    # print("Phase 2")

    # Create a new entry to search the Timed dosage dictionary for the lowest timer
    for vial in timed_dosages:
        timed_dosages[vial]["Elapsed time"] = timed_dosages[vial]['Timer'] - (
                time.perf_counter() - timed_dosages[vial]['Initiated timer'])

    # print(timed_dosages)
    # Sort the timed dictionary based on elapsed time
    find_lowest_timer = min((int(d['Elapsed time'])) for d in timed_dosages.values())

    # print(find_lowest_timer)

    current_experiment = [k for k in timed_dosages if (int(timed_dosages[k]['Elapsed time'])) == find_lowest_timer]

    current_experiment = current_experiment[0]

    # Load all the information
    # print(timed_dosages)
    timed_dosage_volume = timed_dosages[current_experiment]['Volume']
    timed_dosage_x = timed_dosages[current_experiment]['x']
    timed_dosage_y = timed_dosages[current_experiment]['y']
    timed_dosage_pump_number = timed_dosages[current_experiment]['Solvent']

    # Move to the vial
    move_to(timed_dosage_x, timed_dosage_y)

    # Wait untill it is time to dose the solution
    try:
        sleep_time = timed_dosages[current_experiment]['Timer'] - (
                time.perf_counter() - timed_dosages[current_experiment]['Initiated timer'])
        print("Wait for: ", sleep_time)
        time.sleep(sleep_time)
    except:
        pass  # This just makes the code survive a sleep.time with a 0

    # Dose the liquid
    start_experiment_timer = time.time() - start
    pump_objects[timed_dosage_pump_number - 1].dose(timed_dosage_volume)
    duration_timer = time.time() - start - start_experiment_timer
    gantt_timer_dictionary[current_experiment]["Solution {}".format(timed_dosage_pump_number)] = \
        {"Dosing initiated": start_experiment_timer, "Dosing duration": duration_timer}

    temporary_prio_df = pd.DataFrame(prio_df.loc[current_experiment]).T.loc[:,
                        (pd.DataFrame(prio_df.loc[current_experiment]).T != 0).any(axis=0)]
    # Look at the next priority for a dosage
    next_dosage_priority = 'Priority {}'.format(timed_dosages[current_experiment]['Priority'] + 1)
    if int(timed_dosages[current_experiment]['Priority'] + 1) <= len(temporary_prio_df.columns):
        # Set timer for the next dosage inside the timed dosage dictionary, it inherits the vial information for that dosage
        set_next_timer = dosing_data_dictionary[next_dosage_priority][current_experiment]['Timer']
        set_next_volume = dosing_data_dictionary[next_dosage_priority][current_experiment]['Volume']
        set_next_solvent = dosing_data_dictionary[next_dosage_priority][current_experiment]['Solvent']
        set_next_x = dosing_data_dictionary[next_dosage_priority][current_experiment]['x']
        set_next_y = dosing_data_dictionary[next_dosage_priority][current_experiment]['y']
        start_timer = time.perf_counter()

        timed_dosages[current_experiment] = {'Initiated timer': start_timer, 'Timer': set_next_timer,
                                             'Volume': set_next_volume, 'Solvent': set_next_solvent,
                                             'Priority': int(next_dosage_priority[-1]),
                                             'x': set_next_x, 'y': set_next_y}
    else:
        # Remove the vial entry if it is done with dosing that vial completely
        del timed_dosages[current_experiment]

    # Break out if there is no timers left
    if not timed_dosages:
        break
end_sequence(unprime=pump_objects)
# update_gantt_dictionary(gantt_timer_dictionary)