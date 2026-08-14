from datetime import date

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

import db
import images
from export_excel import build_excel
from export_pdf import build_pdf
from ogp import fetch_url_metadata

app = Flask(__name__)
app.secret_key = "ohaka-meshi-local-secret"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

db.init_db()


def _form_data(form):
    is_eating_out = form.get("is_eating_out") == "1"
    return {
        "dish_name": form.get("dish_name", "").strip(),
        "is_eating_out": is_eating_out,
        "restaurant_name": form.get("restaurant_name", "").strip() if is_eating_out else "",
        "location": form.get("location", "").strip() if is_eating_out else "",
        "reference_url": form.get("reference_url", "").strip(),
        "comment": form.get("comment", "").strip(),
        "eaten_date": form.get("eaten_date") or date.today().isoformat(),
    }


def _resolve_screenshot(form, files, existing_filename=None, remove_existing=False):
    uploaded = files.get("screenshot")
    if uploaded and uploaded.filename:
        return images.save_uploaded_image(uploaded)

    ogp_image_url = form.get("ogp_image_url", "").strip()
    if ogp_image_url:
        saved = images.save_image_from_url(ogp_image_url)
        if saved:
            return saved

    if remove_existing:
        return None

    return existing_filename


@app.route("/")
def index():
    return render_template(
        "index.html",
        today=date.today().isoformat(),
        restaurant_names=db.distinct_values("restaurant_name"),
        locations=db.distinct_values("location"),
    )


@app.route("/entries", methods=["GET"])
def entries_list():
    q = request.args.get("q", "").strip()
    type_filter = request.args.get("type", "").strip()
    sort = request.args.get("sort", db.DEFAULT_SORT).strip()
    entries = db.list_entries(q=q or None, type_filter=type_filter or None, sort=sort)
    return render_template("list.html", entries=entries, q=q, type_filter=type_filter, sort=sort)


@app.route("/entries", methods=["POST"])
def entries_create():
    data = _form_data(request.form)
    if not data["dish_name"]:
        flash("料理名を入力してください", "error")
        return redirect(url_for("index"))

    data["screenshot_filename"] = _resolve_screenshot(request.form, request.files)
    db.create_entry(data)
    flash("保存しました", "success")
    return redirect(url_for("index"))


@app.route("/entries/<int:entry_id>")
def entry_detail(entry_id):
    entry = db.get_entry(entry_id)
    if entry is None:
        flash("記録が見つかりませんでした", "error")
        return redirect(url_for("entries_list"))
    return render_template("detail.html", entry=entry)


@app.route("/entries/<int:entry_id>/edit", methods=["GET", "POST"])
def entry_edit(entry_id):
    entry = db.get_entry(entry_id)
    if entry is None:
        flash("記録が見つかりませんでした", "error")
        return redirect(url_for("entries_list"))

    if request.method == "POST":
        data = _form_data(request.form)
        if not data["dish_name"]:
            flash("料理名を入力してください", "error")
            return redirect(url_for("entry_edit", entry_id=entry_id))

        remove_existing = request.form.get("remove_screenshot") == "1"
        new_filename = _resolve_screenshot(
            request.form,
            request.files,
            existing_filename=entry["screenshot_filename"],
            remove_existing=remove_existing,
        )
        if new_filename != entry["screenshot_filename"] and entry["screenshot_filename"]:
            images.delete_image(entry["screenshot_filename"])

        data["screenshot_filename"] = new_filename
        db.update_entry(entry_id, data)
        flash("更新しました", "success")
        return redirect(url_for("entry_detail", entry_id=entry_id))

    return render_template(
        "edit.html",
        entry=entry,
        restaurant_names=db.distinct_values("restaurant_name"),
        locations=db.distinct_values("location"),
    )


@app.route("/entries/<int:entry_id>/delete", methods=["POST"])
def entry_delete(entry_id):
    db.soft_delete_entry(entry_id)
    flash("削除しました", "success")
    return redirect(url_for("entries_list"))


def _entries_from_request_args():
    q = request.args.get("q", "").strip()
    type_filter = request.args.get("type", "").strip()
    sort = request.args.get("sort", db.DEFAULT_SORT).strip()
    return db.list_entries(q=q or None, type_filter=type_filter or None, sort=sort)


@app.route("/export/excel")
def export_excel():
    entries = _entries_from_request_args()
    buffer = build_excel(entries)
    filename = f"ohaka_meshi_{date.today().strftime('%Y%m%d')}.xlsx"
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.route("/export/pdf")
def export_pdf():
    entries = _entries_from_request_args()
    buffer = build_pdf(entries)
    filename = f"ohaka_meshi_{date.today().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")


@app.route("/api/fetch-url-metadata", methods=["POST"])
def api_fetch_url_metadata():
    payload = request.get_json(silent=True) or {}
    url = (payload.get("url") or "").strip()
    return jsonify(fetch_url_metadata(url))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
