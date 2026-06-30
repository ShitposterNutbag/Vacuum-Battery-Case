"""Parametric dimensions for the vacuum battery enclosure.

All dimensions are in millimeters.  The first commit intentionally models a
clean enclosure framework only; tune these values later after measuring the
actual battery pack, charging board, connectors, LEDs, button, and wiring.
"""

# Core modeling units -------------------------------------------------------
UNITS = "mm"

# Enclosure outside dimensions
ENCLOSURE_LENGTH = 140.0
ENCLOSURE_WIDTH = 72.0
BASE_HEIGHT = 36.0
LID_HEIGHT = 8.0
CORNER_RADIUS = 6.0

# Print and assembly clearances
WALL_THICKNESS = 2.0
DEFAULT_CLEARANCE = 0.5
LID_FIT_CLEARANCE = DEFAULT_CLEARANCE
LID_OVERLAP_DEPTH = 4.0
LID_TOP_THICKNESS = WALL_THICKNESS

# Battery placeholder; not fitted to real electronics yet
BATTERY_LENGTH = 118.0
BATTERY_WIDTH = 50.0
BATTERY_HEIGHT = 24.0
BATTERY_CLEARANCE = DEFAULT_CLEARANCE
BATTERY_FLOOR_CLEARANCE = 2.0

# Magnet pockets
MAGNET_DIAMETER = 10.0
MAGNET_DEPTH = 3.0
MAGNET_EDGE_OFFSET_X = 14.0
MAGNET_EDGE_OFFSET_Y = 14.0
MAGNET_COUNT = 4

# Placeholder feature dimensions and locations
USB_BOARD_LENGTH = 24.0
USB_BOARD_WIDTH = 16.0
USB_BOARD_HEIGHT = 4.0
USB_BOARD_CLEARANCE = DEFAULT_CLEARANCE
USB_BOARD_CENTER_X = 0.0
USB_BOARD_CENTER_Y = -(ENCLOSURE_WIDTH / 2.0 - WALL_THICKNESS - 10.0)
USB_BOARD_Z = 8.0
USB_PORT_WIDTH = 10.0
USB_PORT_HEIGHT = 4.0

DC_JACK_DIAMETER = 8.0
DC_JACK_CENTER_X = 32.0
DC_JACK_CENTER_Y = -(ENCLOSURE_WIDTH / 2.0)
DC_JACK_CENTER_Z = 14.0

LED_WINDOW_COUNT = 4
LED_WINDOW_DIAMETER = 3.0
LED_WINDOW_SPACING = 8.0
LED_WINDOW_CENTER_X = -28.0
LED_WINDOW_CENTER_Y = 0.0

PUSH_BUTTON_DIAMETER = 7.0
PUSH_BUTTON_CENTER_X = 28.0
PUSH_BUTTON_CENTER_Y = 0.0

WIRE_CHANNEL_WIDTH = 5.0
WIRE_CHANNEL_DEPTH = 1.2
WIRE_CHANNEL_LENGTH = 90.0
WIRE_CHANNEL_CENTER_X = 0.0
WIRE_CHANNEL_CENTER_Y = 22.0

# Export configuration
GENERATED_DIR = "generated"
EXPORT_STL = True
EXPORT_STEP = True
STL_TOLERANCE = 0.1
STL_ANGULAR_TOLERANCE = 0.1
