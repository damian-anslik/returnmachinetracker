let locations;
let reports;
let markersInViewport = [];

const renderMap = async () => {
  const defaultLocation = [53.35, -6.3];
  const defaultZoom = 11;
  const tileLayerUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  const attributions = {
    openStreetMap:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    icons:
      '<a href="https://www.flaticon.com/free-icons/location" title="location icons">Location icons created by kmg design - Flaticon</a>',
  };
  let map = L.map("map").setView(defaultLocation, defaultZoom);
  if ("geolocation" in navigator) {
    navigator.permissions
      .query({ name: "geolocation" })
      .then((permissionStatus) => {
        if (
          permissionStatus.state === "granted" ||
          permissionStatus.state === "prompt"
        ) {
          navigator.geolocation.getCurrentPosition((position) => {
            userLocation = [
              position.coords.latitude,
              position.coords.longitude,
            ];
            zoomLevel = 14;
            map.setView(userLocation, zoomLevel);
          });
        } else {
          map.setView(defaultLocation, defaultZoom);
        }
      });
  }
  let attribution = `${attributions.openStreetMap} | ${attributions.icons}`;
  L.tileLayer(tileLayerUrl, {
    attribution,
  }).addTo(map);
  return map;
};

const showMapMarker = (map, location, locationReports, show = false) => {
  const showSuccessIndicator = () => {
    reportFeedbackIndicator.hidden = false;
    reportFeedbackIndicator.id = "success-indicator";
    reportFeedbackIndicator.innerText = "Thanks for your report!";
  };

  const showErrorIndicator = () => {
    reportFeedbackIndicator.hidden = false;
    reportFeedbackIndicator.id = "error-indicator";
    reportFeedbackIndicator.style.marginBottom = "0.5rem";
    reportFeedbackIndicator.innerText =
      "Failed to submit report. Please try again.";
  };

  const reportButtonHandler = async () => {
    const response = await fetch(`/reports?location_id=${location.id}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (response.ok) {
      reportButton.hidden = true;
      showSuccessIndicator();
      let userReport = await response.json();
      reports.push(userReport);
      locationReports.push(userReport);
      showMapMarker(map, location, locationReports, true);
    } else {
      showErrorIndicator();
    }
  };

  const mostRecentReport = () => {
    let mostRecentReport = locationReports[0];
    for (let i = 1; i < locationReports.length; i++) {
      if (locationReports[i].created_at > mostRecentReport.created_at) {
        mostRecentReport = locationReports[i];
      }
    }
    return mostRecentReport;
  };

  // Check if user has already reported this location
  let userHasReportedLocation = locationReports.some(
    (report) => report.is_user_report
  );

  // Create a popup for the marker
  let markerPopup = document.createElement("div");

  // Add information about the location
  const locationName = document.createElement("h3");
  locationName.innerText = location.name;
  markerPopup.appendChild(locationName);

  // Show list of reports for this location
  let customIconUrl;
  let iconSizeFactor;
  if (locationReports.length > 0) {
    // Show the time of the most recent report for this location
    let lastReport = mostRecentReport();
    const timestamp = new Date(lastReport.created_at * 1000);
    const localTimestamp = timestamp.toLocaleString();
    const reportText = document.createElement("p");
    reportText.innerText = `Most recent report: ${localTimestamp}`;
    markerPopup.appendChild(reportText);
    // Show the total number of reports for this location
    const totalReports = document.createElement("p");
    totalReports.innerText = `Total reports within last 24 hours: ${locationReports.length}`;
    markerPopup.appendChild(totalReports);

    customIconUrl = "/static/pin-red.png";
    iconSizeFactor = 1.5;
  } else {
    const noReports = document.createElement("p");
    noReports.innerText =
      "No reports for this location within the last 24 hours";
    markerPopup.appendChild(noReports);
    customIconUrl = "/static/pin-blue.png";
    iconSizeFactor = 1.0;
  }

  // Add a visual indicator for the report feedback
  const reportFeedbackIndicator = document.createElement("div");
  reportFeedbackIndicator.hidden = true;
  reportFeedbackIndicator.className = "report-feedback-indicator";
  markerPopup.appendChild(reportFeedbackIndicator);

  // Add a button to report the location
  const reportButton = document.createElement("button");
  reportButton.className = "report-button";
  reportButton.innerText = "Report as unavailable";
  reportButton.onclick = reportButtonHandler;
  markerPopup.appendChild(reportButton);

  if (userHasReportedLocation) {
    reportButton.hidden = true;
    showSuccessIndicator();
  }

  // Configure the marker icon
  let iconHeight = 35;
  let iconWidth = 35;
  customIcon = L.icon({
    iconUrl: customIconUrl,
    iconSize: [iconWidth * iconSizeFactor, iconHeight * iconSizeFactor],
    // iconAnchor: [12, 41],
    popupAnchor: [
      (iconWidth * iconSizeFactor) / 6,
      -iconHeight * iconSizeFactor,
    ],
    tooltipAnchor: [16, -28],
    shadowUrl:
      "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
    shadowSize: [10, 10],
  });
  const marker = L.marker([location.lat, location.long], {
    icon: customIcon,
  }).addTo(map);
  marker.on("click", () => {
    // Zoom in on the marker when clicked
    map.setView([location.lat, location.long], 15);
  });
  marker.bindPopup(markerPopup);
  if (show) {
    marker.openPopup();
  }
  return marker;
};

const fetchReports = async () => {
  const response = await fetch("/reports");
  return response.json();
};

const fetchLocations = async () => {
  const response = await fetch("/locations");
  return response.json();
};

const populateMapMarkers = async (map) => {
  const [reportsResponse, locationsResponse] = await Promise.all([
    fetchReports(),
    fetchLocations(),
  ]);
  const getMapBounds = () => {
    const boundsMargin = 0.01;
    let bounds = map.getBounds();
    bounds._northEast.lat += boundsMargin;
    bounds._northEast.lng += boundsMargin;
    bounds._southWest.lat -= boundsMargin;
    bounds._southWest.lng -= boundsMargin;
    return bounds;
  };
  reports = reportsResponse.reports;
  locations = locationsResponse.locations;

  // Load initial locations
  let initialBounds = getMapBounds();
  let initialLocations = locations.filter((location) =>
    initialBounds.contains([location.lat, location.long])
  );
  markersInViewport = initialLocations.map((location) => {
    let locationReports = reports.filter(
      (report) => report.location_id === location.id
    );
    return {
      marker: showMapMarker(map, location, locationReports),
      location_id: location.id,
    };
  });

  // Load markers for locations in the viewport
  map.on("moveend", () => {
    let currentBounds = getMapBounds();
    let newLocationsInViewport = locations.filter((location) =>
      currentBounds.contains([location.lat, location.long])
    );
    // Remove markers for locations that are no longer in the viewport
    let locationsToRemove = markersInViewport.filter(
      (marker) =>
        !newLocationsInViewport.some(
          (location) => location.id === marker.location_id
        )
    );
    locationsToRemove.forEach((location) => {
      location.marker.remove();
    });
    // Add markers for new locations in the viewport
    newLocationsInViewport.forEach((location) => {
      let locationReports = reports.filter(
        (report) => report.location_id === location.id
      );
      let marker = showMapMarker(map, location, locationReports);
      markersInViewport.push({
        marker: marker,
        location_id: location.id,
      });
    });
  });
};

document.addEventListener("DOMContentLoaded", () => {
  renderMap().then((map) => {
    populateMapMarkers(map).then(() => {
      document
        .getElementsByClassName("loading-indicator-container")[0]
        .remove();
    });
  });
});
