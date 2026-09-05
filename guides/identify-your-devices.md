# Identify your robot and station

Before changing an association, collect the identities of both physical devices. A nearby Bluetooth name can be shared by several devices and is not enough to select a repair target.

1. Inspect the robot and the station labels. Record the marketed model, hardware revision if printed, and the MAC address encoded in each QR label.
2. Scan nearby devices with Re-Pair. Match each inspected address to its radio identity. A CoreBluetooth peripheral UUID is not a MAC address.
3. Read the available component versions. A station can contain more than one processor and more than one firmware version.
4. Select one robot and one station. Compare their roles and exact versions with the application's included capability catalog.

An address match links an inspected label to a radio observation; it does not prove that two stations have the same power supply, contacts, bus wiring or firmware behavior. A photographed or copied QR label alone does not prove current physical presence. The workflow needs a contemporaneous connection and identity read from each selected device.

If a label and radio identity disagree, stop the operation and identify the devices again. Do not automatically reverse the address or substitute a nearby peripheral to make the match succeed. The protocol profile must define any on-wire byte-order conversion.

Local floor or room labels are free and do not change the device's stored name. A persistent name change is a separate capability; it must establish whether that name is stored by the station, robot or vendor cloud.

Examples in this repository use synthetic locally administered addresses, such as `02:00:00:00:00:01`. Do not submit real household MAC addresses in public bug reports.
