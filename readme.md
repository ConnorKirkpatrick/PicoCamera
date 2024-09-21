# Raspberry pi pico camera host. 
This project uses an Raspberry pi pico 2 and a MIPI camera to host a website that streams the cameras view. This is used to provide me with a camera stream from inside my guinea pigs cage

## Features
 * Slim and simple code to allow easy use
 * Customisation of camera to enable rotation, framerate, and definition adjustments
 * Built-in firewall integration for security
    * The program makes use of abuseIPDB and UFW to detect malicious IP connection and blacklist them 
 * DOS mitigations for slower connections
    * Slow connections are automatically dropped by the system to prevent pinning of resources