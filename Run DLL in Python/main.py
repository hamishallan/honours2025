import usb.core
import usb.util

# ARCoptix spectrometer
VENDOR_ID = 0x1b9e
PRODUCT_ID = 0x2002

# Find the device
dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

if dev is None:
    raise ValueError("Device not found")

print("Spectrometer found!")
print("Manufacturer:", usb.util.get_string(dev, dev.iManufacturer))
print("Product:", usb.util.get_string(dev, dev.iProduct))
print("Serial:", usb.util.get_string(dev, dev.iSerialNumber))

# Set configuration (some devices require this)
dev.set_configuration()

# Get the first configuration and interface
cfg = dev.get_active_configuration()
intf = cfg[(0, 0)]

# Print endpoints
for ep in intf.endpoints():
    direction = "IN" if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN else "OUT"
    print("Endpoint address: 0x{:02x}, direction: {}, type: {}".format(
        ep.bEndpointAddress,
        direction,
        usb.util.endpoint_type(ep.bmAttributes)
    ))

# Send vendor command (0x10) to address 0x0000 with 2-byte payload [0x00, 0x00]
result = dev.ctrl_transfer(
    bmRequestType=0x40,  # OUT | VENDOR | DEVICE
    bRequest=0x10,       # command 16
    wValue=0x0000,       # address
    wIndex=0,
    data_or_wLength=[0x00, 0x00]
)
print("SendDataVendorCMD result:", result)


# Read up to 512 bytes from endpoint 0x82 (data)
data = dev.read(0x82, 512, timeout=2000)
print("Data received (len={}):".format(len(data)))
print(list(data[:16]))  # Print first 16 bytes for inspection
