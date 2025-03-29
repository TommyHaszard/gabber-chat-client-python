import objc
from Foundation import NSObject, NSRunLoop
from CoreBluetooth import (
    CBPeripheralManager,
    CBAdvertisementDataServiceUUIDsKey,
    CBMutableService,
    CBMutableCharacteristic,
    CBUUID,
    CBCharacteristicPropertyRead,
    CBAttributePermissionsReadable,
    CBCharacteristicPropertyWriteWithoutResponse,
    CBAttributePermissionsWriteable,
    CBATTRequest,
    CBATTError
)
from typing import List


class BluetoothPeripheral(NSObject):
    def init(self):
        self = objc.super(BluetoothPeripheral, self).init()
        if self is None:
            return None

        self.peripheral_manager = CBPeripheralManager.alloc().initWithDelegate_queue_(self, None)
        self.service_uuid = CBUUID.UUIDWithString_("94F741D6-2671-44C5-978F-AD4CBE94BF1F")  
        self.characteristic_uuid = CBUUID.UUIDWithString_("94F741D6-2671-44C5-978F-AD4CBE94BF20")  
        return self

    def peripheralManagerDidUpdateState_(self, peripheral):
        if peripheral.state() == 5:  # CBManagerStatePoweredOn
            print("Bluetooth is ON. Starting advertisement...")
            self.start_advertising()

    def peripheralManager_didReceiveWriteRequests_(
        self, peripheral: CBPeripheralManager, requests: List[CBATTRequest]
    ):
        request: CBATTRequest = requests[0]
        if request.characteristic().UUID().isEqual_(self.characteristic_uuid):
            self._peripheralData = bytearray(request.value()).decode()
            print(f"didReceiveWriteRequest: Wrote: {self._peripheralData}")
        else:
            print(
                f"didReceiveWriteRequest: {request.central} "
                + f"{request.characteristic().UUID().UUIDString()}. Ignoring"
            )

    def start_advertising(self):
        characteristic = CBMutableCharacteristic.alloc().initWithType_properties_value_permissions_(
            self.characteristic_uuid,
            CBCharacteristicPropertyRead | CBCharacteristicPropertyWriteWithoutResponse,  # Fix: Use correct property enum
            None,
            CBAttributePermissionsReadable | CBAttributePermissionsWriteable,
        )

        service = CBMutableService.alloc().initWithType_primary_(self.service_uuid, True)
        service.setCharacteristics_([characteristic])
        self.peripheral_manager.addService_(service)

        self.peripheral_manager.startAdvertising_({
            CBAdvertisementDataServiceUUIDsKey: [self.service_uuid]
        })
        print(f"Advertising started with service UUID: {self.service_uuid}")

if __name__ == "__main__":
    import AppKit
    app = AppKit.NSApplication.sharedApplication()
    peripheral = BluetoothPeripheral.alloc().init()
    NSRunLoop.currentRunLoop().run()
