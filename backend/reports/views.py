import pandas as pd
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render

from . import services


REPORT_TYPES = {
    "masters": "Master Performance",
    "services": "Revenue by Service",
    "clients": "Client Activity",
    "statuses": "Appointment Status Summary",
}

REPORT_HANDLERS = {
    "masters": services.get_master_performance_report,
    "services": services.get_service_revenue_report,
    "clients": services.get_client_activity_report,
    "statuses": services.get_status_summary_report,
}


def _get_report_data(request):
    report_type = request.GET.get("type", "masters")
    date_from = request.GET.get("date_from") or None
    date_to = request.GET.get("date_to") or None

    handler = REPORT_HANDLERS.get(report_type, services.get_master_performance_report)
    columns, rows = handler(date_from=date_from, date_to=date_to)

    return report_type, date_from, date_to, columns, rows


@staff_member_required
def report_view(request):
    report_type, date_from, date_to, columns, rows = _get_report_data(request)
    report_title = REPORT_TYPES.get(report_type, "Master Performance")

    return render(
        request,
        "reports/reports.html",
        {
            "report_types": REPORT_TYPES,
            "current_type": report_type,
            "report_title": report_title,
            "columns": columns,
            "rows": rows,
            "date_from": date_from or "",
            "date_to": date_to or "",
        },
    )


@staff_member_required
def report_export_view(request):
    report_type, date_from, date_to, columns, rows = _get_report_data(request)
    export_format = request.GET.get("format", "xlsx")

    df = pd.DataFrame(rows, columns=columns)
    filename = f"{report_type}_report"

    if export_format == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
        df.to_csv(response, index=False)
        return response

    if export_format == "json":
        response = HttpResponse(content_type="application/json")
        response["Content-Disposition"] = f'attachment; filename="{filename}.json"'
        df.to_json(response, orient="records", force_ascii=False)
        return response

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    df.to_excel(response, index=False)
    return response
