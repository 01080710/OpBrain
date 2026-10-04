"""Power BI 瀏覽器互動邏輯（凍結，見 trace/decisions.md DEC-001）。

從原 src/collectors/pbi_collector.py 原封不動搬來（2026-10-02 重構）。selector、
dispatch_event 點擊、CDP Page.setDownloadBehavior、以 mtime 偵測下載、日期輸入順序，
每一項都是排除過實際失敗模式後才定案的。未經明確指示並在真實 Power BI 重新驗證，
不得修改。唯一改動：原本寫死的輸出根目錄改成由呼叫端傳入（output_root）。
"""
import time

DOWNLOAD_TIMEOUT_SECONDS = 45


def get_date_inputs(page):
    all_inputs = page.locator("input.date-slicer-datepicker").all()
    start_input = end_input = None
    for inp in all_inputs:
        label = inp.get_attribute("aria-label") or ""
        if "開始日期" in label:
            start_input = inp
        elif "結束日期" in label:
            end_input = inp
    return start_input, end_input


def set_input_value(input_locator, value_str):
    input_locator.fill(value_str)
    input_locator.press("Tab")


def parse_date(d):
    y, m, dd = d.split("/")
    return (int(y), int(m), int(dd))


def set_date_range(page, new_start, new_end):
    start_input, end_input = get_date_inputs(page)
    if start_input is None or end_input is None:
        raise RuntimeError("Could not locate start/end date inputs")

    current_start = start_input.input_value()
    current_end = end_input.input_value()
    cur_start_t, cur_end_t = parse_date(current_start), parse_date(current_end)
    new_start_t, new_end_t = parse_date(new_start), parse_date(new_end)

    if (current_start, current_end) == (new_start, new_end):
        return

    if new_start_t > cur_end_t:
        set_input_value(end_input, new_end)
        set_input_value(start_input, new_start)
    elif new_end_t < cur_start_t:
        set_input_value(start_input, new_start)
        set_input_value(end_input, new_end)
    else:
        set_input_value(start_input, new_start)
        set_input_value(end_input, new_end)

    page.wait_for_timeout(250)
    final_start = start_input.input_value()
    final_end = end_input.input_value()
    if parse_date(final_start) != new_start_t or parse_date(final_end) != new_end_t:
        raise RuntimeError(f"Date did not apply correctly: got {final_start}->{final_end}")


def get_hour_inputs(page):
    wrapper = page.locator(".visual-slicer").filter(has=page.locator("h3[title='hour']"))
    if wrapper.count() == 0:
        return None, None
    inputs = wrapper.locator("input.date-slicer-input")
    return inputs.nth(0), inputs.nth(1)


def set_hour_range(page):
    start_input, end_input = get_hour_inputs(page)
    if start_input is None:
        return

    current_start = start_input.input_value()
    current_end = end_input.input_value()
    if current_start == "0" and current_end == "24":
        return

    set_input_value(end_input, "24")
    set_input_value(start_input, "0")
    page.wait_for_timeout(250)

    final_start = start_input.input_value()
    final_end = end_input.input_value()
    if final_start != "0" or final_end != "24":
        raise RuntimeError(f"Hour did not apply correctly: got {final_start}-{final_end}")


def ensure_row_expanded(page):
    button = page.locator("div.expandCollapseButton").first
    if button.count() == 0:
        return
    icon = button.locator("i.glyphicon").first
    aria = icon.get_attribute("aria-label") if icon.count() > 0 else None
    if aria == "已展開":
        return
    button.dispatch_event("click")
    page.wait_for_timeout(250)


def find_visual_more_options(page):
    page.mouse.move(600, 350)
    page.wait_for_timeout(200)

    candidates = page.get_by_role("button", name="更多選項").all()
    target = None
    for b in candidates:
        box = b.bounding_box()
        if box and box["y"] > 150:
            target = b
    return target


def export_current_page(page, cdp, report_dir, filename):
    cdp.send("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(report_dir)})

    click_time = time.time()

    more_options = find_visual_more_options(page)
    if more_options is None:
        raise RuntimeError("Could not find the visual's '更多選項' button")
    more_options.dispatch_event("click")
    page.wait_for_timeout(250)

    export_item = page.get_by_role("menuitem", name="匯出資料")
    export_item.dispatch_event("click")
    page.wait_for_timeout(400)

    current_config_radio = page.get_by_role("radio", name="具有目前配置的資料")
    if current_config_radio.count() > 0 and not current_config_radio.is_checked():
        current_config_radio.dispatch_event("click")
        page.wait_for_timeout(200)

    export_btn = page.get_by_role("button", name="匯出", exact=True)
    export_btn.click()

    new_file = None
    deadline = time.monotonic() + DOWNLOAD_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        candidates = [
            f for f in report_dir.glob("*")
            if f.is_file()
            and f.stat().st_mtime > click_time
            and not f.name.endswith(".crdownload")
            and not f.name.startswith("~$")
            and f.name.lower().startswith("data")
        ]
        if candidates:
            candidate = max(candidates, key=lambda f: f.stat().st_mtime)
            size1 = candidate.stat().st_size
            time.sleep(0.4)
            size2 = candidate.stat().st_size
            if size1 == size2 and size1 > 0:
                new_file = candidate
                break
        time.sleep(0.2)

    if new_file is None:
        raise RuntimeError("No new file appeared in folder within timeout")

    dest_path = report_dir / filename
    if dest_path.exists():
        dest_path.unlink()

    last_err = None
    for _ in range(8):
        try:
            new_file.rename(dest_path)
            last_err = None
            break
        except PermissionError as e:
            last_err = e
            time.sleep(0.3)
    if last_err is not None:
        raise last_err

    return dest_path


def export_one(page, cdp, date_str, report_name, file_prefix, output_root):
    y, m, d = date_str.split("/")
    date_tag = f"{y}-{int(m):02d}-{int(d):02d}"

    report_dir = output_root / report_name
    report_dir.mkdir(parents=True, exist_ok=True)

    page.keyboard.press("Escape")
    page.wait_for_timeout(100)

    nav_item = page.get_by_text(report_name, exact=True).first
    nav_item.click()
    page.locator("input.date-slicer-datepicker").first.wait_for(state="attached", timeout=10000)
    page.wait_for_timeout(150)

    set_date_range(page, date_str, date_str)
    set_hour_range(page)
    ensure_row_expanded(page)

    filename = f"{file_prefix}_{date_tag}.xlsx"
    return export_current_page(page, cdp, report_dir, filename)
