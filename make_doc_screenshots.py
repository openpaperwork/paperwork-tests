#!/usr/bin/env python3

import os
import sys
import time

import PIL.Image

os.environ['KEEP_ENV'] = "1"
os.environ["LANG"] = "C"

from gi.repository import GLib

import pytestshot

from tests import paperwork

from paperwork_backend.util import rm_rf

OUT_DIRECTORY = "doc_screenshots"


def get_widget_position(widget):
    return widget.translate_coordinates(
        widget.get_toplevel(), 0, 0
    )


def save_sc(filename, image,
            crop_around_widget=None, crop_size=(150, 150),
            add_cursor=False, cursor_offset=10):
    img_size = image.size

    if crop_around_widget:
        position = get_widget_position(crop_around_widget)
        size = (
            crop_around_widget.get_allocated_width(),
            crop_around_widget.get_allocated_height()
        )
        center = (
            min(max(0, position[0] + int(size[0] / 2)), img_size[0]),
            min(max(0, position[1] + int(size[1] / 2)), img_size[1])
        )
        crop = (
            min(max(0, center[0] - crop_size[0]), img_size[0]),
            min(max(0, center[1] - crop_size[1]), img_size[1]),
            min(max(0, center[0] + crop_size[0]), img_size[0]),
            min(max(0, center[1] + crop_size[1]), img_size[1])
        )
        image = image.crop(crop)
        if add_cursor and not isinstance(add_cursor, tuple):
            add_cursor = (center[0] - crop[0] + cursor_offset,
                          center[1] - crop[1] + cursor_offset)

    if add_cursor and not isinstance(add_cursor, tuple):
        add_cursor = (int(img_size[0] / 2), int(img_size[1] / 2))

    if add_cursor:
        cursor = PIL.Image.open("cursor.png")
        image.paste(cursor, add_cursor, cursor)

    image.save(os.path.join(OUT_DIRECTORY, filename))


def gen_adf_access(pw):
    menu = pw.main_window.widget_tree.get_object("menubuttonOtherScans")
    menu.clicked()
    pw.wait()
    time.sleep(1)
    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("adf_access.png", img, menu, add_cursor=True)


def gen_adf_multiscan(pw):
    doc = pw.docsearch.get_doc_from_docid("20121213_1946_26")
    pw.main_window.show_doc(doc)
    pw.wait()

    action = pw.main_window.actions['multi_scan'][1]
    GLib.idle_add(action.do)
    pw.wait()

    try:
        GLib.idle_add(action.dialog.actions['add_doc'][1].do)
        pw.wait()

        treeview = action.dialog.lists['docs']['gui']
        treeview.get_selection().select_path([1])
        pw.wait()
        img = pytestshot.screenshot(action.dialog.window.get_window())
        save_sc("adf_multiscan.png", img, add_cursor=(500, 75))
    finally:
        GLib.idle_add(action.dialog.window.destroy)
    pw.wait()


def gen_adf_settings(pw):
    action = pw.main_window.actions['open_settings'][1]
    GLib.idle_add(action.do)
    time.sleep(3)
    try:
        sources = action.dialog.device_settings['source']['gui']
        GLib.idle_add(sources.popup)
        pw.wait()

        img = pytestshot.screenshot(action.dialog.window.get_window())
        save_sc("adf_settings.png", img, sources, add_cursor=True,
                crop_size=(250, 150))
    finally:
        GLib.idle_add(action.dialog.window.destroy)


def gen_import_pdf(pw):
    menu = pw.main_window.widget_tree.get_object("menubuttonOtherScans")
    pw.wait()
    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("import_pdf_en_0001.png", img, menu, add_cursor=True)

    menu.clicked()
    pw.wait()
    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("import_pdf_en_0002.png", img, menu, add_cursor=True)
    save_sc("paperwork_import.png", img, menu, add_cursor=True)


def gen_import_pdf3(pw):
    action = pw.main_window.actions['import'][1]
    GLib.idle_add(action.do)
    pw.wait()

    try:
        dirpath = os.path.abspath("orig_data/20130126_1833_26")
        action._select_file_dialog.select_filename(os.path.join(dirpath, "doc.pdf"))
        pw.wait()
        img = pytestshot.screenshot(action._select_file_dialog.get_window())
        save_sc("import_pdf_en_0003.png", img, add_cursor=(600, 160))
    finally:
        GLib.idle_add(action._select_file_dialog.destroy)


def gen_import_pdf4(pw):
    doc = pw.docsearch.get_doc_from_docid("20130126_1902_26")
    pw.main_window.show_doc(doc)
    pw.wait()
    time.sleep(1)

    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("import_pdf_en_0004.png", img)


def gen_new_doc(pw):
    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("new_doc.png", img,
            pw.main_window.actions['new_doc'][0][0],
            crop_size=(100, 80), add_cursor=True)


def gen_paperwork_export(pw):
    menu = pw.main_window.widget_tree.get_object("menubuttonWindowAdvanced")
    GLib.idle_add(menu.clicked)
    time.sleep(1)
    pw.wait()
    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("paperwork_export_0001.png", img, menu, add_cursor=True,
            crop_size=(150, 200))
    # XXX(Jflesch): no way to make paperwork_export_0002.png ...


def gen_paperwork_export3(pw):
    doc = pw.docsearch.get_doc_from_docid("20121213_1946_26")
    pw.main_window.show_doc(doc)
    pw.wait()

    action = pw.main_window.actions['open_export_page_dialog'][1]
    GLib.idle_add(action.do)
    time.sleep(3)
    pw.wait()

    GLib.idle_add(
        pw.main_window.export['export_path'].set_text,
        "Documents/out.png"
    )
    GLib.idle_add(pw.main_window.export['buttons']['ok'].set_sensitive, True)
    pw.wait()

    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("paperwork_export_0003.png", img,
            pw.main_window.export['buttons']['ok'],
            add_cursor=True,
            crop_size=(300, 150))


def gen_goto_labels_and_memo(pw):
    doc = pw.docsearch.get_doc_from_docid("20130126_1902_26")
    pw.main_window.show_doc(doc)
    pw.wait()
    time.sleep(1)

    doclist = pw.main_window.doclist.gui['list']
    row = doclist.get_selected_rows()[0]
    row_children = row.get_children()[0].get_children()
    buttons = row_children[2]  # thumbnail, docname+labels, >buttons<
    button = buttons.get_children()[0]

    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("goto_labels_and_memo.png", img, button, add_cursor=True,
            crop_size=(300, 300), cursor_offset=2)


def gen_label_and_memo(pw):
    doc = pw.docsearch.get_doc_from_docid("20130126_1902_26")
    pw.main_window.show_doc(doc)
    pw.wait()
    time.sleep(1)

    GLib.idle_add(pw.main_window.switch_leftpane, 'doc_properties')
    pw.wait()

    scrollbars = pw.main_window.widget_tree.get_object("box_left_docproperties")
    vadj = scrollbars.get_vadjustment()
    GLib.idle_add(vadj.set_value, vadj.get_upper())
    pw.wait()

    memo = pw.main_window.doc_properties_panel.widgets['extra_keywords']

    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("label_and_memo.png", img, memo, crop_size=(300, 200))


def gen_paperwork_scan(pw):
    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("paperwork_scan.png", img,
            pw.main_window.actions['single_scan'][0][0],
            crop_size=(100, 100), add_cursor=True)


def gen_paperwork_search(pw):
    field = pw.main_window.actions['search'][0][0]
    GLib.idle_add(field.set_text, "contrat")
    time.sleep(2)
    pw.wait()

    img = pytestshot.screenshot(pw.gdk_window)
    save_sc("paperwork_search.png", img, field,
            crop_size=(200, 200), add_cursor=True)


SCREENSHOTS = {
    "adf_access": gen_adf_access,
    "adf_multiscan": gen_adf_multiscan,
    "adf_settings": gen_adf_settings,
    "import_pdf": gen_import_pdf,
    "import_pdf3": gen_import_pdf3,
    "import_pdf4": gen_import_pdf4,
    "new_doc": gen_new_doc,
    "export": gen_paperwork_export,
    "export3": gen_paperwork_export3,
    "goto_labels_and_memo": gen_goto_labels_and_memo,
    "label_and_memo": gen_label_and_memo,
    "paperwork_scan": gen_paperwork_scan,
    "paperwork_search": gen_paperwork_search,
}


def main(argv):
    args = argv[1:]

    if args == []:
        rm_rf(OUT_DIRECTORY)
    try:
        os.mkdir(OUT_DIRECTORY)
    except:
        pass

    for (sc_name, sc_method) in SCREENSHOTS.items():
        if args != [] and sc_name not in args:
            continue

        paperwork_inst = paperwork.PaperworkInstance()
        paperwork_inst.start()
        try:
            time.sleep(3)
            paperwork_inst.wait()
            sc_method(paperwork_inst)
            paperwork_inst.wait()
        finally:
            paperwork_inst.stop()


if __name__ == "__main__":
    main(sys.argv)
