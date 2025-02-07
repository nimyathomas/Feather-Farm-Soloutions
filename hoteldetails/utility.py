from math import radians, sin, cos, sqrt, atan2
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import googlemaps
from datetime import datetime
import osmnx as ox
from geopy.distance import geodesic
import networkx as nx

def calculate_distance(origin, destination):
    """
    Calculate the distance between two points on Earth in kilometers.
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = radians(origin[0]), radians(origin[1])
    lat2, lon2 = radians(destination[0]), radians(destination[1])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    r = 6371  # Radius of Earth in kilometers
    return c * r


def send_order_confirmation_email(email, order):
    """Send an order confirmation email to the user."""
    subject = f"Order Confirmation - #{order.id}"
    context = {
        "order": order,
        "delivery_date": order.delivery_date,
        "total_price": f"${order.price:.2f}",
        "delivery_option": order.delivery_option,
    }

    # Render email content
    html_message = render_to_string("emails/order_confirmation.html", context)
    plain_message = strip_tags(html_message)
    from_email = "nimyathomas3@gmail.com"  # Use your email address

    send_mail(subject, plain_message, from_email, [email], html_message=html_message)

def get_travel_time_with_traffic(origin, destination, api_key):
    gmaps = googlemaps.Client(key=api_key)
    now = datetime.now()
    directions_result = gmaps.directions(origin, destination, departure_time=now, traffic_model='best_guess')
    
    if directions_result:
        return directions_result[0]['legs'][0]['duration_in_traffic']['value'] / 60  # Return time in minutes
    return None

def get_travel_time_and_distance(origin, destination):
    # Ensure origin and destination are tuples of (latitude, longitude)
    if len(origin) != 2 or len(destination) != 2:
        raise ValueError("Origin and destination must be tuples of (latitude, longitude)")

    # Get the graph for the area
    G = ox.graph_from_point(origin, dist=10000, network_type='drive')  # Adjust distance as needed

    # Get the nearest nodes to the origin and destination
    orig_node = ox.distance.nearest_nodes(G, origin[1], origin[0])  # (lon, lat)
    dest_node = ox.distance.nearest_nodes(G, destination[1], destination[0])  # (lon, lat)

    # Calculate the shortest path
    route = nx.shortest_path(G, orig_node, dest_node, weight='travel_time')

    # Calculate distance using geodesic
    distance = geodesic(origin, destination).kilometers  # Distance in kilometers

    # Calculate travel time based on the route
    travel_time = sum(G.edges[edge].get('travel_time', 0) for edge in zip(route[:-1], route[1:]))

    return distance, travel_time
