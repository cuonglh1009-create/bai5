"""
MSSV: 202418859
Họ tên: Lê Hùng Cường
KIỂM CHỨNG CÁC YÊU CẦU CỦA ĐỀ BÀI (unittest)
Chạy:  python -m unittest test_requirements -v
"""
import inspect
import unittest
from datetime import datetime

from main import (Device, DeviceStatus, INetworkable, Computer, Printer,
                  NetworkPrinter, Projector, LabRoom)

NOW = datetime.now().year


def make_pc(id="PC", year=None, price=10_000_000, gpu=False, **kw):
    return Computer(id, "PC", NOW - 1 if year is None else year, price, 8, "i5", gpu, **kw)


def make_printer(id="PR", year=None, price=5_000_000, pages=0, color=False, ptype="laser"):
    return Printer(id, "PR", NOW - 1 if year is None else year, price, ptype, pages, color)


def make_projector(id="PJ", year=None, price=10_000_000, hours=0):
    return Projector(id, "PJ", NOW - 1 if year is None else year, price, 3000, hours)


# ---------------------------------------------------------------- 3.1 Device
class TestDevice(unittest.TestCase):
    def test_device_la_lop_truu_tuong(self):
        with self.assertRaises(TypeError):
            Device("D1", "x", NOW, 1)

    def test_ma_thiet_bi_rong_bi_tu_choi(self):
        for bad in ("", "   "):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                make_pc(id=bad)

    def test_gia_mua_phai_lon_hon_0(self):
        for bad in (0, -1, -1000):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                make_pc(price=bad)
        self.assertEqual(make_pc(price=1).purchase_price, 1)  # biên: nhỏ nhất hợp lệ

    def test_nam_su_dung_khong_lon_hon_nam_hien_tai(self):
        with self.assertRaises(ValueError):
            make_pc(year=NOW + 1)
        self.assertEqual(make_pc(year=NOW).year_of_use, NOW)  # biên: đúng năm hiện tại

    def test_ma_thiet_bi_chi_set_khi_khoi_tao(self):
        d = make_pc(id="PC01")
        self.assertEqual(d.device_id, "PC01")
        with self.assertRaises(AttributeError):
            d.device_id = "KHAC"
        self.assertEqual(d.device_id, "PC01")

    def test_trang_thai_mac_dinh_va_enum(self):
        self.assertEqual(make_pc().status, DeviceStatus.Active)
        self.assertEqual({s.name for s in DeviceStatus},
                         {"Active", "UnderMaintenance", "Retired"})
        self.assertEqual(make_pc(status=DeviceStatus.Retired).status, DeviceStatus.Retired)

    def test_phuong_thuc_tinh_chi_phi_la_truu_tuong(self):
        self.assertIn("calculate_annual_maintenance_cost", Device.__abstractmethods__)

    def test_lop_con_khong_cai_dat_chi_phi_thi_khong_tao_duoc(self):
        class Thieu(Device):
            pass
        with self.assertRaises(TypeError):
            Thieu("X", "x", NOW, 1)

    def test_ghi_de_str(self):
        for d in (make_pc("A"), make_printer("B"), make_projector("C")):
            with self.subTest(cls=type(d).__name__):
                self.assertIn(d.device_id, str(d))
                self.assertIn(d.name, str(d))
                self.assertNotIn("object at 0x", str(d))
        self.assertIn("RAM", str(make_pc()))
        self.assertIn("lumen", str(make_projector()))
        self.assertIn("trang", str(make_printer()))


# --------------------------------------------------- 3.2 Chi phí bảo trì
class TestComputerCost(unittest.TestCase):
    def test_co_ban_5_phan_tram(self):
        self.assertAlmostEqual(make_pc(price=10_000_000).calculate_annual_maintenance_cost(), 500_000)

    def test_gpu_roi_cong_2_phan_tram(self):
        self.assertAlmostEqual(make_pc(price=10_000_000, gpu=True).calculate_annual_maintenance_cost(), 700_000)

    def test_tren_5_nam_cong_1_phan_tram_bien(self):
        self.assertAlmostEqual(make_pc(year=NOW - 5).calculate_annual_maintenance_cost(), 500_000)  # đúng 5 năm: KHÔNG cộng
        self.assertAlmostEqual(make_pc(year=NOW - 6).calculate_annual_maintenance_cost(), 600_000)  # 6 năm: cộng

    def test_ca_gpu_va_tren_5_nam(self):
        self.assertAlmostEqual(make_pc(year=NOW - 8, gpu=True).calculate_annual_maintenance_cost(), 800_000)


class TestPrinterCost(unittest.TestCase):
    def test_co_ban_4_phan_tram(self):
        self.assertAlmostEqual(make_printer(price=5_000_000).calculate_annual_maintenance_cost(), 200_000)

    def test_tren_100000_trang_bien(self):
        self.assertAlmostEqual(make_printer(pages=100_000).calculate_annual_maintenance_cost(), 200_000)  # đúng 100.000: KHÔNG
        self.assertAlmostEqual(make_printer(pages=100_001).calculate_annual_maintenance_cost(), 700_000)

    def test_may_in_mau_cong_300000(self):
        self.assertAlmostEqual(make_printer(color=True).calculate_annual_maintenance_cost(), 500_000)

    def test_ca_hai_phu_phi(self):
        self.assertAlmostEqual(make_printer(pages=120_000, color=True).calculate_annual_maintenance_cost(), 1_000_000)

    def test_loai_may_in_chi_laser_hoac_phun(self):
        make_printer(ptype="laser"); make_printer(ptype="phun")
        with self.assertRaises(ValueError):
            make_printer(ptype="kim")


class TestProjectorCost(unittest.TestCase):
    def test_co_ban_3_phan_tram(self):
        self.assertAlmostEqual(make_projector(price=10_000_000).calculate_annual_maintenance_cost(), 300_000)

    def test_tren_3000_gio_bien(self):
        self.assertAlmostEqual(make_projector(hours=3000).calculate_annual_maintenance_cost(), 300_000)  # đúng 3.000: KHÔNG
        self.assertAlmostEqual(make_projector(hours=3001).calculate_annual_maintenance_cost(), 1_800_000)


# ------------------------------------------------------ 4. INetworkable
class TestInterface(unittest.TestCase):
    def test_phan_loai_thuc_thi_interface(self):
        self.assertIsInstance(make_pc(), INetworkable)                     # Computer: có
        self.assertNotIsInstance(make_printer(), INetworkable)             # Printer thường: không
        self.assertNotIsInstance(make_projector(), INetworkable)           # Projector: không
        np_ = NetworkPrinter("N", "n", NOW - 1, 1000, "laser", 0)
        self.assertIsInstance(np_, INetworkable)                           # NetworkPrinter: có
        self.assertIsInstance(np_, Printer)                                # và vẫn là Printer
        self.assertIsInstance(np_, Device)

    def test_interface_khong_khoi_tao_truc_tiep(self):
        with self.assertRaises(TypeError):
            INetworkable()


def networkables():
    return [make_pc("PC"), NetworkPrinter("NP", "n", NOW - 1, 1000, "laser", 0)]


class TestConnection(unittest.TestCase):
    def test_trang_thai_ban_dau(self):
        for n in networkables():
            with self.subTest(cls=type(n).__name__):
                self.assertFalse(n.is_connected)
                self.assertIsNone(n.ip_address)

    def test_ket_noi_thanh_cong(self):
        for n in networkables():
            with self.subTest(cls=type(n).__name__):
                n.connect("192.168.1.5")
                self.assertTrue(n.is_connected)
                self.assertEqual(n.ip_address, "192.168.1.5")

    def test_ip_rong_bi_tu_choi(self):
        for n in networkables():
            for bad in ("", "   ", None):
                with self.subTest(cls=type(n).__name__, bad=bad), self.assertRaises(ValueError):
                    n.connect(bad)
                self.assertFalse(n.is_connected)

    def test_khong_ket_noi_lai_khi_dang_ket_noi(self):
        for n in networkables():
            with self.subTest(cls=type(n).__name__):
                n.connect("10.0.0.1")
                with self.assertRaises(RuntimeError):
                    n.connect("10.0.0.2")
                self.assertEqual(n.ip_address, "10.0.0.1")  # IP cũ giữ nguyên

    def test_ngat_ket_noi_is_connected_false_va_mat_ip(self):
        for n in networkables():
            with self.subTest(cls=type(n).__name__):
                n.connect("10.0.0.1")
                n.disconnect()
                self.assertFalse(n.is_connected)
                self.assertIsNone(n.ip_address)

    def test_ket_noi_lai_duoc_sau_khi_ngat(self):
        for n in networkables():
            with self.subTest(cls=type(n).__name__):
                n.connect("10.0.0.1"); n.disconnect(); n.connect("10.0.0.9")
                self.assertTrue(n.is_connected)
                self.assertEqual(n.ip_address, "10.0.0.9")

    def test_ngat_khi_chua_ket_noi_khong_loi(self):
        for n in networkables():
            n.disconnect()
            self.assertFalse(n.is_connected)


# ------------------------------------------------------------ 5. LabRoom
class TestLabRoom(unittest.TestCase):
    def setUp(self):
        self.room = LabRoom("R1", "Lab 1", 30)

    def test_thong_tin_phong(self):
        self.assertEqual((self.room.room_id, self.room.name, self.room.capacity), ("R1", "Lab 1", 30))

    def test_them_va_tim_thiet_bi(self):
        pc = make_pc("PC01")
        self.room.add_device(pc)
        self.assertIs(self.room.find_device("PC01"), pc)
        self.assertIsNone(self.room.find_device("KHONG_CO"))

    def test_quy_tac_1_khong_them_trung_ma(self):
        self.room.add_device(make_pc("PC01"))
        with self.assertRaises(ValueError):
            self.room.add_device(make_printer("PC01"))   # khác loại nhưng trùng mã
        self.assertEqual(self.room.calculate_annual_maintenance_cost(),
                         make_pc("x").calculate_annual_maintenance_cost())  # chỉ còn 1 thiết bị

    def test_trung_ma_o_phong_khac_van_duoc(self):
        other = LabRoom("R2", "Lab 2", 20)
        pc = make_pc("PC01")
        self.room.add_device(pc)
        other.add_device(make_pc("PC01"))   # không ném lỗi: quy tắc chỉ áp dụng trong một phòng

    def test_quy_tac_2_khong_chap_nhan_null(self):
        with self.assertRaises(ValueError):
            self.room.add_device(None)

    def test_remove_device(self):
        self.room.add_device(make_pc("PC01"))
        self.assertTrue(self.room.remove_device("PC01"))
        self.assertIsNone(self.room.find_device("PC01"))
        self.assertFalse(self.room.remove_device("PC01"))      # xóa lần 2
        self.assertFalse(self.room.remove_device("KHONG_CO"))

    def test_thiet_bi_ton_tai_sau_khi_go_khoi_phong_ket_tap(self):
        pc = make_pc("PC01")
        self.room.add_device(pc)
        self.room.remove_device("PC01")
        self.assertEqual(pc.device_id, "PC01")           # đối tượng vẫn dùng được
        LabRoom("R2", "Lab 2", 10).add_device(pc)        # và thêm được vào phòng khác

    def test_phong_rong_chi_phi_bang_0(self):
        self.assertEqual(self.room.calculate_annual_maintenance_cost(), 0)

    def test_tong_chi_phi(self):
        self.room.add_device(make_pc("A", year=NOW - 8, price=15_000_000, gpu=True))      # 1.200.000
        self.room.add_device(make_printer("B", price=5_000_000, pages=120_000, color=True))  # 1.000.000
        self.room.add_device(make_projector("C", price=10_000_000, hours=3500))           # 1.800.000
        self.assertAlmostEqual(self.room.calculate_annual_maintenance_cost(), 4_000_000)

    def test_quy_tac_3_da_hinh_khong_dung_isinstance(self):
        src = inspect.getsource(LabRoom.calculate_annual_maintenance_cost)
        for banned in ("isinstance", "type(", "__class__", "switch", "match "):
            self.assertNotIn(banned, src)

    def test_quy_tac_3_loai_thiet_bi_moi_khong_can_sua_LabRoom(self):
        class Scanner(Device):
            def calculate_annual_maintenance_cost(self):
                return 123_456
        self.room.add_device(Scanner("S1", "scanner", NOW, 1000))
        self.assertAlmostEqual(self.room.calculate_annual_maintenance_cost(), 123_456)

    def test_quy_tac_4_thiet_bi_can_bao_tri(self):
        under = make_printer("UM"); under.status = DeviceStatus.UnderMaintenance   # điều kiện 1
        old = make_pc("OLD", year=NOW - 6)                                          # điều kiện 2
        both = make_pc("BOTH", year=NOW - 9, status=DeviceStatus.UnderMaintenance)  # cả hai
        edge = make_pc("EDGE", year=NOW - 5)                                        # đúng 5 năm: KHÔNG
        new = make_pc("NEW")                                                        # không
        retired = make_pc("RET", status=DeviceStatus.Retired)                       # không
        for d in (under, old, both, edge, new, retired):
            self.room.add_device(d)
        ids = {d.device_id for d in self.room.get_devices_requiring_maintenance()}
        self.assertEqual(ids, {"UM", "OLD", "BOTH"})

    def test_quy_tac_4_khong_trung_lap_va_phong_rong(self):
        self.assertEqual(self.room.get_devices_requiring_maintenance(), [])
        self.room.add_device(make_pc("BOTH", year=NOW - 9, status=DeviceStatus.UnderMaintenance))
        self.assertEqual(len(self.room.get_devices_requiring_maintenance()), 1)


# ------------------------------------------------ 6. Kịch bản kiểm thử tối thiểu
class TestKichBanMuc6(unittest.TestCase):
    def test_toan_bo_kich_ban(self):
        pc1 = Computer("PC01", "Dell", 2018, 15_000_000, 16, "i5", True)
        pc2 = Computer("PC02", "HP", NOW - 1, 12_000_000, 8, "i3", False)
        pr1 = NetworkPrinter("PR01", "Canon", NOW - 2, 5_000_000, "laser", 120_000, True)
        pr2 = Printer("PR02", "Epson", NOW - 1, 3_000_000, "phun", 5_000)
        pj = Projector("PJ01", "Sony", 2019, 10_000_000, 3500, 3500)
        r1, r2 = LabRoom("R1", "L1", 30), LabRoom("R2", "L2", 25)
        for d in (pc1, pr1, pj): r1.add_device(d)
        for d in (pc2, pr2): r2.add_device(d)
        with self.assertRaises(ValueError):
            r1.add_device(make_pc("PC01"))
        self.assertGreater(r1.calculate_annual_maintenance_cost(), r2.calculate_annual_maintenance_cost())
        self.assertEqual({d.device_id for d in r1.get_devices_requiring_maintenance()} & {"PC01", "PJ01"},
                         {"PC01", "PJ01"})
        # duyệt qua kiểu INetworkable, không phụ thuộc lớp cụ thể
        nets = [d for d in (pc1, pc2, pr1, pr2, pj) if isinstance(d, INetworkable)]
        self.assertEqual(len(nets), 3)
        for i, n in enumerate(nets):
            n.connect(f"192.168.1.{i}")
        self.assertTrue(all(n.is_connected for n in nets))


if __name__ == "__main__":
    unittest.main(verbosity=2)