#Make sure the ASM_protocol_library is in the same folder as this file.
import ASM_protocol_library

############### standard protocol ###############

ASM_protocol_library.start_sequence(10,3,offset=True,pump=True)

ASM_protocol_library.standard_dosage(speed=100)

ASM_protocol_library.end_sequence(3)

############### calibration protocol ###############

# ASM_protocol_library.start_sequence(10,1,offset=True,pump=True)

# ASM_protocol_library.calibration_dosage

# ASM_protocol_library.end_sequence(1)

