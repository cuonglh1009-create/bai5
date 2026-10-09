"""
MSSV: 202418859
Họ tên: Lê Hùng Cường
HỆ THỐNG QUẢN LÝ THIẾT BỊ
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import List, Optional


class DeviceStatus(Enum):
    Active = "Active"
    UnderMaintenance = "UnderMaintenance"
    Retired = "Retired"


class INetworkable(ABC):
    @property
    @abstractmethod
    def ip_address(self) -> Optional[str]:
        pass

    @abstractmethod
    def connect(self, ip_address: str) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        pass


class Device(ABC):
    def __init__(self, device_id: str, name: str, year_of_use: int, purchase_price: float,
                 status: DeviceStatus = DeviceStatus.Active):
        if not device_id or device_id.strip() == "":
            raise ValueError("Mã thiết bị không được rỗng")
        if purchase_price <= 0:
            raise ValueError("Giá mua phải lớn hơn 0")
        current_year = datetime.now().year
        if year_of_use > current_year:
            raise ValueError(f"Năm đưa vào sử dụng không được lớn hơn năm hiện tại ({current_year})")

        self._device_id = device_id  # chỉ set khi khởi tạo
        self.name = name
        self.year_of_use = year_of_use
        self.purchase_price = purchase_price
        self.status = status

    @property
    def device_id(self) -> str:
        return self._device_id

    @abstractmethod
    def calculate_annual_maintenance_cost(self) -> float:
        pass

    def years_in_use(self) -> int:
        return datetime.now().year - self.year_of_use

    def __str__(self) -> str:
        return (f"[{self.device_id}] {self.name} | Năm: {self.year_of_use} | "
                f"Giá: {self.purchase_price:,.0f} | Trạng thái: {self.status.value}")


class Computer(Device, INetworkable):
    def __init__(self, device_id: str, name: str, year_of_use: int, purchase_price: float,
                 ram_gb: int, cpu_type: str, has_discrete_gpu: bool,
                 status: DeviceStatus = DeviceStatus.Active):
        super().__init__(device_id, name, year_of_use, purchase_price, status)
        self.ram_gb = ram_gb
        self.cpu_type = cpu_type
        self.has_discrete_gpu = has_discrete_gpu
        self._ip_address: Optional[str] = None
        self._is_connected: bool = False

    def calculate_annual_maintenance_cost(self) -> float:
        cost = 0.05 * self.purchase_price  # 5%
        if self.has_discrete_gpu:
            cost += 0.02 * self.purchase_price  # +2%
        if self.years_in_use() > 5:
            cost += 0.01 * self.purchase_price  # +1%
        return cost

    @property
    def ip_address(self) -> Optional[str]:
        return self._ip_address

    def connect(self, ip_address: str) -> None:
        if not ip_address or ip_address.strip() == "":
            raise ValueError("Địa chỉ IP không được rỗng")
        if self._is_connected:
            raise RuntimeError("Thiết bị đang kết nối, không thể kết nối lại")
        self._ip_address = ip_address
        self._is_connected = True

    def disconnect(self) -> None:
        self._is_connected = False
        self._ip_address = None
    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def __str__(self) -> str:
        gpu = "Có GPU rời" if self.has_discrete_gpu else "Không GPU rời"
        base = super().__str__()
        return f"{base} | RAM: {self.ram_gb}GB | CPU: {self.cpu_type} | {gpu}"


class Printer(Device):
    def __init__(self, device_id: str, name: str, year_of_use: int, purchase_price: float,
                 printer_type: str, pages_printed: int, is_color: bool = False,
                 status: DeviceStatus = DeviceStatus.Active):
        super().__init__(device_id, name, year_of_use, purchase_price, status)
        if printer_type not in ("laser", "phun"):
            raise ValueError("Loại máy in phải là 'laser' hoặc 'phun'")
        self.printer_type = printer_type
        self.pages_printed = pages_printed
        self.is_color = is_color

    def calculate_annual_maintenance_cost(self) -> float:
        cost = 0.04 * self.purchase_price  # 4%
        if self.pages_printed > 100000:
            cost += 500000
        if self.is_color:
            cost += 300000
        return cost

    def __str__(self) -> str:
        color = "Màu" if self.is_color else "Đen trắng"
        base = super().__str__()
        return f"{base} | Loại: {self.printer_type} | Đã in: {self.pages_printed:,} trang | {color}"


class NetworkPrinter(Printer, INetworkable):
    """Mô hình: chỉ một số máy in có khả năng mạng -> tách lớp NetworkPrinter"""

    def __init__(self, device_id: str, name: str, year_of_use: int, purchase_price: float,
                 printer_type: str, pages_printed: int, is_color: bool = False,
                 status: DeviceStatus = DeviceStatus.Active):
        super().__init__(device_id, name, year_of_use, purchase_price, printer_type, pages_printed, is_color, status)
        self._ip_address: Optional[str] = None
        self._is_connected: bool = False

    @property
    def ip_address(self) -> Optional[str]:
        return self._ip_address

    def connect(self, ip_address: str) -> None:
        if not ip_address or ip_address.strip() == "":
            raise ValueError("Địa chỉ IP không được rỗng")
        if self._is_connected:
            raise RuntimeError("Thiết bị đang kết nối, không thể kết nối lại")
        self._ip_address = ip_address
        self._is_connected = True

    def disconnect(self) -> None:
        self._is_connected = False
        self._ip_address = None

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def __str__(self) -> str:
        return super().__str__() + " | Có hỗ trợ mạng"


class Projector(Device):
    def __init__(self, device_id: str, name: str, year_of_use: int, purchase_price: float,
                 brightness_lumen: int, lamp_hours: int,
                 status: DeviceStatus = DeviceStatus.Active):
        super().__init__(device_id, name, year_of_use, purchase_price, status)
        self.brightness_lumen = brightness_lumen
        self.lamp_hours = lamp_hours

    def calculate_annual_maintenance_cost(self) -> float:
        cost = 0.03 * self.purchase_price  # 3%
        if self.lamp_hours > 3000:
            cost += 1500000
        return cost

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base} | Độ sáng: {self.brightness_lumen} lumen | Giờ bóng đèn: {self.lamp_hours:,}"


class LabRoom:
    def __init__(self, room_id: str, name: str, capacity: int):
        self.room_id = room_id
        self.name = name
        self.capacity = capacity
        self._devices: List[Device] = []

    def add_device(self, device: Device) -> None:
        if device is None:
            raise ValueError("Không chấp nhận thiết bị null")
        self._devices.append(device)

    def remove_device(self, device_id: str) -> bool:
        for i, d in enumerate(self._devices):
            if d.device_id == device_id:
                del self._devices[i]
                return True
        return False

    def find_device(self, device_id: str) -> Optional[Device]:
        for d in self._devices:
            if d.device_id == device_id:
                return d
        return None

    def calculate_annual_maintenance_cost(self) -> float:
        total = 0.0
        for device in self._devices:
            if isinstance(device, Computer):
                total += device.calculate_annual_maintenance_cost()
            elif isinstance(device, Printer):
                total += device.calculate_annual_maintenance_cost()
            elif isinstance(device, Projector):
                total += device.calculate_annual_maintenance_cost()
        return total

    def get_devices_requiring_maintenance(self) -> List[Device]:
        result = []
        for device in self._devices:
            if device.status == DeviceStatus.UnderMaintenance:
                result.append(device)
        return result

    def list_devices(self) -> None:
        print(f"\n=== Phòng {self.room_id} - {self.name} (Sức chứa: {self.capacity}) ===")
        if not self._devices:
            print("  (Không có thiết bị)")
        for d in self._devices:
            print(f"  - {d}")

    def __str__(self) -> str:
        return f"LabRoom[{self.room_id}] {self.name} | Sức chứa: {self.capacity} | Số TB: {len(self._devices)}"

#  GIAO DIỆN MENU CONSOLE

def print_menu():
    print("  HỆ THỐNG QUẢN LÝ THIẾT BỊ & BẢO TRÌ")
    print("  1. Tạo thiết bị mới")
    print("  2. Tạo phòng thực hành")
    print("  3. Thêm thiết bị vào phòng")
    print("  4. Xóa thiết bị khỏi phòng")
    print("  5. Xem danh sách thiết bị trong phòng")
    print("  6. Tính chi phí bảo trì của phòng")
    print("  7. Liệt kê thiết bị cần bảo trì")
    print("  8. Kết nối mạng (INetworkable)")
    print("  9. Ngắt kết nối mạng")
    print(" 10. Xem tất cả thiết bị đã tạo")
    print("  0. Thoát")


def create_device(devices: list):
    print("\n--- Tạo thiết bị ---")
    print("  a. Máy tính (Computer)")
    print("  b. Máy in (Printer)")
    print("  c. Máy in mạng (NetworkPrinter)")
    print("  d. Máy chiếu (Projector)")
    kind = input("Chọn loại (a/b/c/d): ").strip().lower()

    try:
        device_id = input("Mã thiết bị: ").strip()
        name = input("Tên thiết bị: ").strip()
        year = int(input("Năm đưa vào sử dụng: "))
        price = float(input("Giá mua: "))

        if kind == "a":
            ram = int(input("RAM (GB): "))
            cpu = input("Loại CPU: ").strip()
            gpu = input("Có GPU rời? (y/n): ").strip().lower() == "y"
            device = Computer(device_id, name, year, price, ram, cpu, gpu)
        elif kind == "b":
            ptype = input("Loại máy in (laser/phun): ").strip().lower()
            pages = int(input("Số trang đã in: "))
            color = input("Máy in màu? (y/n): ").strip().lower() == "y"
            device = Printer(device_id, name, year, price, ptype, pages, color)
        elif kind == "c":
            ptype = input("Loại máy in (laser/phun): ").strip().lower()
            pages = int(input("Số trang đã in: "))
            color = input("Máy in màu? (y/n): ").strip().lower() == "y"
            device = NetworkPrinter(device_id, name, year, price, ptype, pages, color)
        elif kind == "d":
            lumen = int(input("Độ sáng (lumen): "))
            hours = int(input("Số giờ bóng đèn: "))
            device = Projector(device_id, name, year, price, lumen, hours)
        else:
            print("Lựa chọn không hợp lệ!")
            return

        devices.append(device)
        print(f"✓ Đã tạo: {device}")
    except ValueError as e:
        print(f"✗ Lỗi: {e}")
    except Exception as e:
        print(f"✗ Lỗi nhập liệu: {e}")


def create_lab(labs: list):
    print("\n--- Tạo phòng thực hành ---")
    try:
        room_id = input("Mã phòng: ").strip()
        name = input("Tên phòng: ").strip()
        capacity = int(input("Sức chứa: "))
        lab = LabRoom(room_id, name, capacity)
        labs.append(lab)
        print(f"✓ Đã tạo: {lab}")
    except Exception as e:
        print(f"✗ Lỗi: {e}")


def find_lab(labs: list) -> Optional[LabRoom]:
    if not labs:
        print("Chưa có phòng nào!")
        return None
    print("Danh sách phòng:")
    for i, lab in enumerate(labs):
        print(f"  {i + 1}. {lab}")
    try:
        idx = int(input("Chọn số phòng: ")) - 1
        if 0 <= idx < len(labs):
            return labs[idx]
    except ValueError:
        pass
    print("Lựa chọn không hợp lệ!")
    return None


def find_device_from_list(devices: list) -> Optional[Device]:
    if not devices:
        print("Chưa có thiết bị nào!")
        return None
    print("Danh sách thiết bị:")
    for i, d in enumerate(devices):
        print(f"  {i + 1}. {d}")
    try:
        idx = int(input("Chọn số thiết bị: ")) - 1
        if 0 <= idx < len(devices):
            return devices[idx]
    except ValueError:
        pass
    print("Lựa chọn không hợp lệ!")
    return None


def main_menu():
    devices: List[Device] = []
    labs: List[LabRoom] = []

    while True:
        print_menu()
        choice = input("Chọn chức năng: ").strip()

        if choice == "0":
            print("Tạm biệt!")
            break

        elif choice == "1":
            create_device(devices)

        elif choice == "2":
            create_lab(labs)

        elif choice == "3":
            lab = find_lab(labs)
            if lab is None:
                continue
            device = find_device_from_list(devices)
            if device is None:
                continue
            try:
                lab.add_device(device)
                print(f"✓ Đã thêm {device.device_id} vào {lab.room_id}")
            except ValueError as e:
                print(f"✗ {e}")

        elif choice == "4":
            lab = find_lab(labs)
            if lab is None:
                continue
            device_id = input("Nhập mã thiết bị cần xóa: ").strip()
            if lab.remove_device(device_id):
                print(f"✓ Đã xóa {device_id}")
            else:
                print(f"✗ Không tìm thấy {device_id} trong phòng")

        elif choice == "5":
            lab = find_lab(labs)
            if lab:
                lab.list_devices()

        elif choice == "6":
            lab = find_lab(labs)
            if lab:
                cost = lab.calculate_annual_maintenance_cost()
                print(f"→ Tổng chi phí bảo trì năm của {lab.room_id}: {cost:,.0f} VND")

        elif choice == "7":
            lab = find_lab(labs)
            if lab:
                needing = lab.get_devices_requiring_maintenance()
                print(f"\nThiết bị cần bảo trì ({len(needing)}):")
                if not needing:
                    print("  (Không có)")
                for d in needing:
                    print(f"  - {d}")

        elif choice == "8":
            device = find_device_from_list(devices)
            if device is None:
                continue
            if not isinstance(device, INetworkable):
                print("✗ Thiết bị này không hỗ trợ kết nối mạng!")
                continue
            ip = input("Nhập địa chỉ IP: ").strip()
            try:
                device.connect(ip)
                print(f"✓ Đã kết nối {device.device_id} → {ip}")
            except (ValueError, RuntimeError) as e:
                print(f"✗ {e}")

        elif choice == "9":
            device = find_device_from_list(devices)
            if device is None:
                continue
            if not isinstance(device, INetworkable):
                print("✗ Thiết bị này không hỗ trợ kết nối mạng!")
                continue
            device.disconnect()
            print(f"✓ Đã ngắt kết nối {device.device_id}")
            print(f"  is_connected = {device.is_connected}, IP = {device.ip_address}")

        elif choice == "10":
            print(f"\n--- Tất cả thiết bị đã tạo ({len(devices)}) ---")
            if not devices:
                print("  (Chưa có)")
            for d in devices:
                net_info = ""
                if isinstance(d, INetworkable):
                    net_info = f" | Net: {d.is_connected} / {d.ip_address}"
                print(f"  - {d}{net_info}")

        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn lại!")


if __name__ == "__main__":
    main_menu()
