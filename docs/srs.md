**TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM  
Hệ thống quản lý phiếu bảo hành – Mekong Mobile (luồng L2)**

| **Thông tin** | **Nội dung**                     |
|---------------|----------------------------------|
| Sinh viên     | Lê Thị Thùy Ngân - 2374802010328 |
| Track         | SE – Công nghệ Phần mềm          |
| Học phần      | Chuyên đề Tốt nghiệp 1           |
| Phiên bản     | 0.2                              |

# 1. Giới thiệu

## 1.1 Mục đích và phạm vi

**Bối cảnh:** Tại trung tâm bảo hành của Mekong Mobile, khi khách hàng gửi yêu cầu bảo hành, nhân viên tiếp nhận ghi nhận yêu cầu đó thành một phiếu bảo hành trên giấy. Do phiếu lưu trên giấy nên khó xác định phiếu đang ở bước nào, ai đang xử lý và đã quá hạn cam kết với khách hàng hay chưa (theo tài liệu case study Mekong Mobile).

**Mục đích:** Tài liệu này mô tả yêu cầu cho hệ thống quản lý phiếu bảo hành, để nhân viên ghi nhận, theo dõi phiếu từ lúc tiếp nhận đến khi hoàn tất và biết phiếu nào sắp hoặc đã quá hạn.

**Phạm vi:** Nhân viên tiếp nhận ghi nhận yêu cầu bảo hành của khách hàng, phân loại theo loại lỗi, gán kỹ thuật viên xử lý và theo dõi trạng thái cho đến khi hoàn tất hoặc quá hạn cam kết.

## 1.2 Ngoài phạm vi

- Đăng nhập và phân quyền người dùng (QT-14, QT-15).

- Thiết bị, số serial/IMEI và kiểm tra bảo hành (QT-03, QT-05); phân biệt nhiều trung tâm bảo hành (hệ thống dùng một danh sách phiếu chung).

- Lịch làm việc của kỹ thuật viên (luồng L4) và kho linh kiện (luồng L5).

- Quay lui trạng thái phiếu; các trạng thái Đã phân công, Chờ linh kiện, Đã đóng, Đã hủy của case study.

## 1.3 Bảng thuật ngữ

Mỗi khái niệm chỉ dùng một tên duy nhất trong toàn bộ tài liệu, sơ đồ và mã nguồn.

| **Thuật ngữ**    | **Định nghĩa**                                                                                                 | **Tên trong CSDL**      |
|------------------|----------------------------------------------------------------------------------------------------------------|-------------------------|
| Phiếu bảo hành   | Hồ sơ ghi nhận một yêu cầu bảo hành của khách, có mã duy nhất.                                                 | ticket                  |
| Kỹ thuật viên    | Người được gán xử lý phiếu; là dữ liệu của hệ thống, không phải người dùng.                                    | technician              |
| Loại lỗi         | Nhóm sự cố của phiếu, chọn trong danh sách cố định (xem mục 2.4).                                              | issue_category          |
| Trạng thái phiếu | Một trong ba giá trị: Mới tiếp nhận, Đang xử lý, Hoàn tất.                                                     | ticket.status           |
| Hạn cam kết      | Thời điểm hệ thống cam kết hoàn tất phiếu, tính từ lúc tiếp nhận theo mức ưu tiên (xem mục 2.4).               | ticket.due_date         |
| Quá hạn          | Phiếu chưa Hoàn tất mà đã qua hạn cam kết; do hệ thống tự tính, không phải trạng thái.                         | tính từ ticket.due_date |
| Khách hàng       | Người gửi yêu cầu bảo hành, được nhận diện bằng số điện thoại.                                                 | customer                |
| Sắp đến hạn      | Phiếu chưa Hoàn tất, chưa quá hạn và còn ≤ 12 giờ đến hạn cam kết; do hệ thống tự tính, không phải trạng thái. | tính từ ticket.due_date |
| Mức ưu tiên      | Mức khẩn của phiếu, một trong CAO, TRUNG_BINH, THAP; quyết định hạn cam kết.                                   | ticket.priority         |

# 2. Mô tả tổng quan

## 2.1 Người dùng (actor)

| **Actor**           | **Vai trò**                                                                                                                    |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------|
| Nhân viên tiếp nhận | Tạo phiếu, phân loại, gán kỹ thuật viên, cập nhật trạng thái, xem hạn cam kết, tra cứu khách hàng, xem và lọc danh sách phiếu. |
| Quản lý trung tâm   | Xem danh sách phiếu, lọc theo trạng thái hoặc quá hạn.                                                                         |

## 2.2 Giả định

Phiếu chỉ có ba trạng thái Mới tiếp nhận → Đang xử lý → Hoàn tất, chuyển một chiều. Case study còn có các trạng thái Đã phân công, Chờ linh kiện, Đã đóng và Đã hủy nhưng tài liệu này không dùng: Đã phân công đã có trường kỹ thuật viên thể hiện, Chờ linh kiện thuộc luồng kho linh kiện (L5), còn Đã đóng và Đã hủy nằm ngoài phạm vi luồng tiếp nhận. Quá hạn và sắp đến hạn là kết quả hệ thống tự tính từ hạn cam kết, không phải trạng thái. Khách hàng được nhận diện theo số điện thoại: số đã có thì dùng lại hồ sơ cũ, chưa có thì tạo hồ sơ mới. Hệ thống không có đăng nhập, hai vai trò dùng chung một giao diện.

## 2.3 Ràng buộc

- Công nghệ: ứng dụng web; back-end Python, front-end HTML/CSS/JavaScript, cơ sở dữ liệu MongoDB. Mô hình dữ liệu thiết kế theo dạng collection, chuẩn hóa mức 3NF.

- Dữ liệu: dùng một phần bộ dữ liệu mẫu của case study (phiếu bảo hành lịch sử, kỹ thuật viên, nhóm sự cố) nạp vào MongoDB; hệ thống chạy cục bộ (prototype), đóng gói để chạy bằng tối đa 2 lệnh. Triển khai công khai (ví dụ Render) chỉ làm thêm nếu còn thời gian.

## 2.4 Quy tắc nghiệp vụ và dữ liệu của phiếu

- Hạn cam kết (QT-04) = thời điểm tiếp nhận phiếu (lúc tạo phiếu) + 24 giờ nếu mức ưu tiên CAO, 72 giờ nếu TRUNG_BINH, 120 giờ nếu THAP; chỉ tính ngày làm việc (thứ Hai đến thứ Bảy, không tính Chủ nhật).

- Số điện thoại (QT-01, QT-02): chuẩn hóa về 10 chữ số bắt đầu bằng 0 trước khi lưu (chấp nhận +84…, 84…, có dấu cách hoặc dấu chấm); mỗi số chỉ có một hồ sơ khách.

- Trạng thái (QT-06): chỉ chuyển theo một chiều Mới tiếp nhận → Đang xử lý → Hoàn tất; mỗi lần chuyển được ghi lại thời điểm cùng trạng thái trước và sau.

- Không xóa (QT-13): hệ thống không có chức năng xóa phiếu, hồ sơ khách hay kỹ thuật viên.

| **Trường**    | **Bắt buộc**     | **Quy tắc**                                                                        |
|---------------|------------------|------------------------------------------------------------------------------------|
| Mã phiếu      | Tự sinh          | Duy nhất, không trùng; dạng BH-000231/2026.                                        |
| Tên khách     | Có               | Văn bản, ≤ 120 ký tự.                                                              |
| Số điện thoại | Có               | Chuẩn hóa về 10 chữ số bắt đầu bằng 0 (QT-02); duy nhất trong hồ sơ khách (QT-01). |
| Mô tả lỗi     | Có               | Văn bản, 10–2000 ký tự.                                                            |
| Mức ưu tiên   | Không (mặc định) | Một trong CAO / TRUNG_BINH / THAP; mặc định TRUNG_BINH.                            |
| Loại lỗi      | Không lúc tạo    | Một trong 6 giá trị cố định (MAN_HINH, PIN, SAC, PHAN_MEM, NUOC_VAO, KHAC).        |

# 3. Yêu cầu chức năng

## 3.1 User Story và mức ưu tiên MoSCoW

| **Mã** | **User Story**                                                                                                                                                | **MoSCoW** |
|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|
| US1    | Là nhân viên tiếp nhận, tôi muốn tạo phiếu bảo hành mới từ yêu cầu của khách để mọi yêu cầu đều được lưu lại và có mã để truy vết.                            | MUST       |
| US2    | Là nhân viên tiếp nhận, tôi muốn phân loại phiếu bảo hành theo loại lỗi để biết phiếu thuộc nhóm lỗi nào.                                                     | SHOULD     |
| US3    | Là nhân viên tiếp nhận, tôi muốn gán phiếu bảo hành cho một kỹ thuật viên cụ thể để mỗi phiếu có người chịu trách nhiệm xử lý.                                | MUST       |
| US4    | Là nhân viên tiếp nhận, tôi muốn cập nhật trạng thái của phiếu bảo hành để mọi người biết phiếu đang ở bước nào.                                              | MUST       |
| US5    | Là nhân viên tiếp nhận, tôi muốn xem hạn cam kết của từng phiếu kèm cảnh báo sắp đến hạn hoặc quá hạn để ưu tiên xử lý phiếu gấp.                             | SHOULD     |
| US6    | Là quản lý trung tâm, tôi muốn xem danh sách phiếu kèm trạng thái, hạn cam kết và lọc theo trạng thái hoặc quá hạn để nhanh chóng tìm ra phiếu cần can thiệp. | SHOULD     |
| US7    | Là nhân viên tiếp nhận, tôi muốn tra cứu khách hàng theo số điện thoại để tránh tạo trùng hồ sơ khách.                                                        | COULD      |

## 3.2 Tiêu chí chấp nhận (Given–When–Then) cho story MUST

***US1 – Tạo phiếu bảo hành mới (MUST)***

**GWT1 (thành công) –** Given nhân viên tiếp nhận nhập đủ tên khách, số điện thoại và mô tả lỗi (mức ưu tiên để mặc định hoặc đã chọn),

When nhân viên bấm lưu,

Then hệ thống tạo phiếu với mã tự sinh, trạng thái "Mới tiếp nhận", chưa có kỹ thuật viên, tính hạn cam kết theo mức ưu tiên, và hiển thị mã phiếu cho nhân viên.

**GWT2 (ngoại lệ: thiếu thông tin) –** Given nhân viên bỏ trống một trong ba trường bắt buộc (tên khách, số điện thoại, mô tả lỗi),

When bấm lưu,

Then hệ thống không tạo phiếu và báo rõ trường nào còn thiếu.

**GWT3 (ngoại lệ: sai định dạng) –** Given số điện thoại sau khi chuẩn hóa vẫn không đủ 10 chữ số bắt đầu bằng 0,

When bấm lưu,

Then hệ thống từ chối và báo lỗi định dạng số điện thoại.

***US3 – Gán kỹ thuật viên cho phiếu (MUST)***

**GWT4 (thành công) –** Given phiếu chưa "Hoàn tất" và danh sách kỹ thuật viên có sẵn,

When nhân viên chọn một kỹ thuật viên và xác nhận,

Then phiếu lưu tên kỹ thuật viên đó và trạng thái của phiếu giữ nguyên.

**GWT5 (thành công: đổi người) –** Given phiếu đã có kỹ thuật viên và chưa "Hoàn tất",

When nhân viên chọn kỹ thuật viên khác và xác nhận,

Then phiếu được gán cho người mới, và hệ thống lưu lại việc đổi người (từ ai sang ai, lúc nào).

**GWT6 (ngoại lệ: phiếu đã đóng) –** Given phiếu đã "Hoàn tất",

When nhân viên cố gán hoặc đổi kỹ thuật viên,

Then hệ thống từ chối và báo phiếu đã đóng.

***US4 – Cập nhật trạng thái phiếu (MUST)***

**GWT7 (thành công) –** Given phiếu "Mới tiếp nhận",

When nhân viên chuyển sang "Đang xử lý",

Then hệ thống lưu trạng thái mới cùng thời điểm thay đổi.

**GWT8 (ngoại lệ: nhảy cóc trạng thái) –** Given phiếu đang "Mới tiếp nhận",

When nhân viên chuyển thẳng sang "Hoàn tất",

Then hệ thống từ chối vì sai thứ tự trạng thái.

## 3.3 Yêu cầu chức năng (FR)

| **Mã** | **Mô tả**                                                                                                                                                                                                                                                                                                               |
|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FR-01  | Hệ thống cho phép tạo phiếu bảo hành mới từ tên khách, số điện thoại, mô tả lỗi và mức ưu tiên; chuẩn hóa số điện thoại, gắn phiếu vào hồ sơ khách có sẵn (tạo hồ sơ mới nếu chưa có), tự sinh mã phiếu, đặt trạng thái "Mới tiếp nhận", tính hạn cam kết theo mức ưu tiên và ghi dòng đầu tiên vào lịch sử trạng thái. |
| FR-02  | Hệ thống từ chối tạo phiếu khi thiếu trường bắt buộc hoặc số điện thoại sau chuẩn hóa vẫn sai định dạng, và báo rõ lý do.                                                                                                                                                                                               |
| FR-03  | Hệ thống cho phép phân loại phiếu theo 6 loại lỗi định sẵn.                                                                                                                                                                                                                                                             |
| FR-04  | Hệ thống cho phép gán hoặc đổi kỹ thuật viên cho phiếu chưa hoàn tất, lưu lịch sử đổi người, và từ chối khi phiếu đã hoàn tất.                                                                                                                                                                                          |
| FR-05  | Hệ thống chỉ cho chuyển trạng thái theo một chiều Mới tiếp nhận → Đang xử lý → Hoàn tất, và ghi lại thời điểm cùng trạng thái trước và sau của mỗi lần chuyển.                                                                                                                                                          |
| FR-06  | Hệ thống hiển thị hạn cam kết của từng phiếu kèm cảnh báo sắp đến hạn và quá hạn.                                                                                                                                                                                                                                       |
| FR-07  | Hệ thống cho phép tra cứu khách hàng theo số điện thoại.                                                                                                                                                                                                                                                                |
| FR-08  | Hệ thống hiển thị danh sách phiếu kèm trạng thái và hạn cam kết.                                                                                                                                                                                                                                                        |
| FR-09  | Hệ thống cho phép lọc danh sách phiếu theo trạng thái hoặc quá hạn.                                                                                                                                                                                                                                                     |

# 4. Yêu cầu phi chức năng

| **Mã** | **Nhóm**      | **Mô tả**                                                                                  | **Cách đo**                                     |
|--------|---------------|--------------------------------------------------------------------------------------------|-------------------------------------------------|
| NFR-01 | Hiệu năng     | Tạo một phiếu phản hồi trong ≤ 2 giây ở ≥ 95% lượt gọi, trên dữ liệu mẫu khoảng 100 phiếu. | 20 lượt gọi bằng Postman                        |
| NFR-02 | Khả năng dùng | Nhân viên tạo xong một phiếu hoàn chỉnh trong ≤ 1 phút.                                    | Tự bấm giờ 5 lần                                |
| NFR-03 | Tính duy nhất | Mã phiếu không trùng ở 100% các lần tạo.                                                   | Tạo 20 phiếu liên tiếp, kiểm tra không trùng mã |
| NFR-04 | Hiệu năng     | Hiển thị danh sách khoảng 100 phiếu trong ≤ 3 giây.                                        | Đo thời gian phản hồi bằng Postman              |

# 5. Bảng truy vết

| **FR** | **US** | **Use case**                           | **MoSCoW** |
|--------|--------|----------------------------------------|------------|
| FR-01  | US1    | Tạo phiếu bảo hành mới                 | MUST       |
| FR-02  | US1    | Tạo phiếu bảo hành mới                 | MUST       |
| FR-03  | US2    | Phân loại phiếu theo loại lỗi          | SHOULD     |
| FR-04  | US3    | Gán kỹ thuật viên cho phiếu            | MUST       |
| FR-05  | US4    | Cập nhật trạng thái phiếu              | MUST       |
| FR-06  | US5    | Xem hạn cam kết của phiếu              | SHOULD     |
| FR-07  | US7    | Tra cứu khách hàng theo số điện thoại  | COULD      |
| FR-08  | US6    | Xem danh sách phiếu                    | SHOULD     |
| FR-09  | US6    | Lọc phiếu theo trạng thái hoặc quá hạn | SHOULD     |