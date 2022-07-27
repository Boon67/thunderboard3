import json

class thunderBoard:
    def __init__(self):
        return None

    SERVICE = {
        "GENERIC_ACCESS": "00001800-0000-1000-8000-00805f9b34fb",
        "GENERIC_ATTRIBUTE": "00001801-0000-1000-8000-00805f9b34fb",
        "DEVICE_INFORMATION": "0000180a-0000-1000-8000-00805f9b34fb",
        "BATTERY": "0000180f-0000-1000-8000-00805f9b34fb",
        "AUTOMATION_IO": "00001815-0000-1000-8000-00805f9b34fb",
        "CSC": "00001816-0000-1000-8000-00805f9b34fb",
        "ENVIRONMENT_SENSING": "0000181a-0000-1000-8000-00805f9b34fb",
        "ACCELERATION_ORIENTATION": "a4e649f4-4be5-11e5-885d-feff819cdc9f",
        "AMBIENT_LIGHT": "d24c4f4e-17a7-4548-852c-abf51127368b",
        "INDOOR_AIR_QUALITY": "efd658ae-c400-ef33-76e7-91b00019103b",
        # Magnetic Field Service
        "HALL_EFFECT": "f598dbc5-2f00-4ec5-9936-b3d1aa4f957f",
        "USER_INTERFACE": "fcb89c40-c600-59f3-7dc3-5ece444a401b",
        "POWER_MANAGEMENT": "ec61a454-ed00-a5e8-b8f9-de9ec026ec51"
    }

    CHARACTERISTIC = {
        # Generic Access Service,
        "DEVICE_NAME": "00002a00-0000-1000-8000-00805f9b34fb",
        "APPEARANCE": "00002a01-0000-1000-8000-00805f9b34fb",
        "ATTRIBUTE_CHANGED": "00002a05-0000-1000-8000-00805f9b34fb",
        "SYSTEM_ID": "00002a23-0000-1000-8000-00805f9b34fb",
        # Device Information Service,
        "MODEL_NUMBER": "00002a24-0000-1000-8000-00805f9b34fb",
        # Device Information Service,
        "SERIAL_NUMBER": "00002a25-0000-1000-8000-00805f9b34fb",
        "FIRMWARE_REVISION": "00002a26-0000-1000-8000-00805f9b34fb",
        "HARDWARE_REVISION": "00002a27-0000-1000-8000-00805f9b34fb",
        "MANUFACTURER_NAME": "00002a29-0000-1000-8000-00805f9b34fb",
        # Battery Service,
        "BATTERY_LEVEL": "00002a19-0000-1000-8000-00805f9b34fb",
        "POWER_SOURCE": "EC61A454-ED01-A5E8-B8F9-DE9EC026EC51",
        "CSC_CONTROL_POINT": "00002a55-0000-1000-8000-00805f9b34fb",  # CSC Service,
        "CSC_MEASUREMENT": "00002a5b-0000-1000-8000-00805f9b34fb",
        "CSC_FEATURE": "00002a5c-0000-1000-8000-00805f9b34fb",
        "CSC_UNKNOWN": "9f70a8fc-826c-4c6f-9c72-41b81d1c9561",
        "UV_INDEX": "00002a76-0000-1000-8000-00805f9b34fb",
        # Environment Service,
        "PRESSURE": "00002a6d-0000-1000-8000-00805f9b34fb",
        "TEMPERATURE": "00002a6e-0000-1000-8000-00805f9b34fb",
        # Environment Service,
        "HUMIDITY": "00002a6f-0000-1000-8000-00805f9b34fb",
        # Ambient Light Service for React board,
        "AMBIENT_LIGHT_REACT": "c8546913-bfd9-45eb-8dde-9f8754f4a32e",
        # Ambient Light Service for Sense board,
        "AMBIENT_LIGHT_SENSE": "c8546913-bf01-45eb-8dde-9f8754f4a32e",
        "SOUND_LEVEL": "c8546913-bf02-45eb-8dde-9f8754f4a32e",
        "ENV_CONTROL_POINT": "c8546913-bf03-45eb-8dde-9f8754f4a32e",
        "CO2_READING": "efd658ae-c401-ef33-76e7-91b00019103b",
        "TVOC_READING": "efd658ae-c402-ef33-76e7-91b00019103b",
        "AIR_QUALITY_CONTROL_POINT": "efd658ae-c403-ef33-76e7-91b00019103b",
        "HALL_STATE": "f598dbc5-2f01-4ec5-9936-b3d1aa4f957f",
        "HALL_FIELD_STRENGTH": "f598dbc5-2f02-4ec5-9936-b3d1aa4f957f",  # ,
        "HALL_CONTROL_POINT": "f598dbc5-2f03-4ec5-9936-b3d1aa4f957f",
        # Accelarion and Orientation Service,
        "ACCELERATION": "c4c1f6e2-4be5-11e5-885d-feff819cdc9f",
        "ORIENTATION": "b7c4b694-bee3-45dd-ba9f-f3b5e994f49a",
        "CALIBRATE": "71e30b8c-4131-4703-b0a0-b0bbba75856b",
        "PUSH_BUTTONS": "fcb89c40-c601-59f3-7dc3-5ece444a401b",
        "LEDS": "fcb89c40-c602-59f3-7dc3-5ece444a401b",
        "RGB_LEDS": "fcb89c40-c603-59f3-7dc3-5ece444a401b",
        "UI_CONTROL_POINT": "fcb89c40-c604-59f3-7dc3-5ece444a401b",
        # Automation IO Service,
        "DIGITAL": "00002a56-0000-1000-8000-00805f9b34fb"
    }

    DESCRIPTOR = {"CLIENT_CHARACTERISTIC_CONFIGURATION": "00002902-0000-1000-8000-00805f9b34fb",  # Descriptors,
                "CHARACTERISTIC_PRESENTATION_FORMAT": "00002904-0000-1000-8000-00805f9b34fb"}
