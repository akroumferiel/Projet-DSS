from flask import Flask, render_template, request
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

app = Flask(__name__)
XML_FILE = "transport.xml"


# returns a dict of station id -> station name
def station_map():
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    return {s.attrib["id"]: s.attrib["name"] for s in root.findall("stations/station")}


# load xml using minidom (DOM)
def load_dom():
    return minidom.parse(XML_FILE)


# load xml using elementtree
def load_et():
    tree = ET.parse(XML_FILE)
    return tree.getroot()


# convert a DOM trip node to a python dict
def dom_trip_to_dict(trip_node, smap, line_code, dep_id, arr_id):
    code  = trip_node.getAttribute("code")
    ttype = trip_node.getAttribute("type")

    # get schedules
    schedules = []
    for s in trip_node.getElementsByTagName("schedule"):
        schedules.append({
            "departure": s.getAttribute("departure"),
            "arrival":   s.getAttribute("arrival"),
        })

    # get classes and prices
    classes = []
    for c in trip_node.getElementsByTagName("class"):
        classes.append({
            "type":  c.getAttribute("type"),
            "price": c.getAttribute("price"),
        })

    days_nodes = trip_node.getElementsByTagName("days")
    days = days_nodes[0].firstChild.nodeValue.strip() if days_nodes else ""

    return {
        "code":      code,
        "type":      ttype,
        "line_code": line_code,
        "departure": smap.get(dep_id, dep_id),
        "arrival":   smap.get(arr_id, arr_id),
        "schedules": schedules,
        "classes":   classes,
        "days":      days,
    }


# returns all trips as a list of dicts using elementtree
def get_all_trips_et():
    root = load_et()
    smap = station_map()
    result = []

    for line in root.findall("lines/line"):
        line_code = line.attrib["code"]
        dep_city  = smap.get(line.attrib["departure"], line.attrib["departure"])
        arr_city  = smap.get(line.attrib["arrival"],   line.attrib["arrival"])

        for trip in line.findall("trips/trip"):
            schedules = []
            for s in trip.findall("schedule"):
                schedules.append({
                    "departure": s.attrib["departure"],
                    "arrival":   s.attrib["arrival"],
                })

            classes = []
            for c in trip.findall("class"):
                classes.append({
                    "type":  c.attrib["type"],
                    "price": c.attrib["price"],
                })

            days_el = trip.find("days")
            days = days_el.text.strip() if days_el is not None else ""

            result.append({
                "code":      trip.attrib["code"],
                "type":      trip.attrib["type"],
                "line_code": line_code,
                "departure": dep_city,
                "arrival":   arr_city,
                "schedules": schedules,
                "classes":   classes,
                "days":      days,
            })

    return result


# home page: show all lines using elementtree
@app.route("/")
def index():
    root = load_et()
    smap = station_map()
    lines = []

    for line in root.findall("lines/line"):
        lines.append({
            "id":         line.attrib["code"],
            "departure":  smap.get(line.attrib["departure"], line.attrib["departure"]),
            "arrival":    smap.get(line.attrib["arrival"],   line.attrib["arrival"]),
            "trip_count": len(line.findall("trips/trip")),
        })

    return render_template("index.html", lines=lines)


# search a trip by its code using DOM (minidom)
@app.route("/search", methods=["GET", "POST"])
def search():
    trip  = None
    error = None

    if request.method == "POST":
        code = request.form.get("code", "").strip()

        if not code:
            error = "Please enter a trip code."
        else:
            doc  = load_dom()
            smap = station_map()
            found = lcode = ldep = larr = None

            # search all lines for the trip code
            for line_node in doc.getElementsByTagName("line"):
                for trip_node in line_node.getElementsByTagName("trip"):
                    if trip_node.getAttribute("code") == code:
                        found = trip_node
                        lcode = line_node.getAttribute("code")
                        ldep  = line_node.getAttribute("departure")
                        larr  = line_node.getAttribute("arrival")
                        break
                if found:
                    break

            if found:
                trip = dom_trip_to_dict(found, smap, lcode, ldep, larr)
            else:
                error = f'No trip found with code "{code}".'

    return render_template("trip_detail.html", trip=trip, error=error)


# filter trips by departure, arrival, type and max price
@app.route("/filter", methods=["GET", "POST"])
def filter_trips():
    all_trips = get_all_trips_et()
    results   = []
    filtered  = False

    cities      = sorted(set(t["departure"] for t in all_trips) | set(t["arrival"] for t in all_trips))
    train_types = sorted(set(t["type"] for t in all_trips))

    sel_departure  = ""
    sel_arrival    = ""
    sel_train_type = ""
    sel_max_price  = ""

    if request.method == "POST":
        sel_departure  = request.form.get("departure_city",  "").strip()
        sel_arrival    = request.form.get("arrival_city",    "").strip()
        sel_train_type = request.form.get("train_type",      "").strip()
        sel_max_price  = request.form.get("max_price",       "").strip()
        filtered = True

    elif request.method == "GET":
        # also handle filter from view trips button (GET params)
        sel_departure  = request.args.get("departure_city",  "").strip()
        sel_arrival    = request.args.get("arrival_city",    "").strip()
        sel_train_type = request.args.get("train_type",      "").strip()
        sel_max_price  = request.args.get("max_price",       "").strip()
        if sel_departure or sel_arrival or sel_train_type or sel_max_price:
            filtered = True

    if filtered:
        for trip in all_trips:
            if sel_departure and trip["departure"] != sel_departure:
                continue
            if sel_arrival and trip["arrival"] != sel_arrival:
                continue
            if sel_train_type and trip["type"] != sel_train_type:
                continue
            # check price: keep trip if its cheapest class is within max price
            if sel_max_price:
                try:
                    max_p = float(sel_max_price)
                    min_price = min(float(c["price"]) for c in trip["classes"]) if trip["classes"] else float("inf")
                    if min_price > max_p:
                        continue
                except ValueError:
                    pass
            results.append(trip)

    return render_template("filter_results.html",
        results=results,
        filtered=filtered,
        cities=cities,
        train_types=train_types,
        sel_departure=sel_departure,
        sel_arrival=sel_arrival,
        sel_train_type=sel_train_type,
        sel_max_price=sel_max_price,
    )


# statistics: cheapest/expensive per line + trips per train type
@app.route("/statistics")
def statistics():
    root = load_et()
    smap = station_map()
    stats        = []
    global_types = {}

    for line in root.findall("lines/line"):
        line_code = line.attrib["code"]
        dep = smap.get(line.attrib["departure"], line.attrib["departure"])
        arr = smap.get(line.attrib["arrival"],   line.attrib["arrival"])

        cheapest  = None
        expensive = None
        min_price = float("inf")
        max_price = float("-inf")
        type_count = {}

        for trip in line.findall("trips/trip"):
            tcode = trip.attrib["code"]
            ttype = trip.attrib["type"]

            type_count[ttype]   = type_count.get(ttype, 0) + 1
            global_types[ttype] = global_types.get(ttype, 0) + 1

            for cls in trip.findall("class"):
                p  = float(cls.attrib["price"])
                ct = cls.attrib["type"]

                if p < min_price:
                    min_price = p
                    cheapest  = {"code": tcode, "type": ttype, "class": ct, "price": int(p)}

                if p > max_price:
                    max_price = p
                    expensive = {"code": tcode, "type": ttype, "class": ct, "price": int(p)}

        stats.append({
            "line_code":      line_code,
            "departure":      dep,
            "arrival":        arr,
            "cheapest":       cheapest,
            "most_expensive": expensive,
            "type_count":     type_count,
        })

    return render_template("statistics.html", stats=stats, global_type=global_types)


if __name__ == "__main__":
    app.run(debug=True)
