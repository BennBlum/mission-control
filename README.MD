
# Mission Control

**Mission Control** is a real-time aircraft tracking application that fetches Automatic Dependent Surveillance Broadcasting (ADS-B) data from the OpenSky API. This data is relayed to a Next.js dashboard that features an interactive map, enabling users to track commercial aircraft in near real-time.


# Demo
<img src="demo.gif" alt="Demo" style="width:60%;">
<p>Demo of the Mission Control application</p>

<a href="docs/mission-control-sequence.png" target="_blank">
    <img src="docs/mission-control-sequence.png" alt="Sequence Diagram" style="width:60%;">
</a>
<p><a href="docs/mission-control-sequence.png" target="_blank">Sequence Diagram</a></p>


## Features

- **Real-time Tracking:** Visualize aircraft movements on a dynamic map using ADS-B data.
- **Data Relay:** Utilizes RabbitMQ to efficiently pass data from the OpenSky integration to a FastAPI backend.
- **Next.js Dashboard:** A user-friendly interface for displaying tracking data.


## Work in Progress

This project is currently under development, and future updates will include integration of additional data sources beyond ADS-B. Check back for updates!

## License

This project is licensed under the MIT License.

