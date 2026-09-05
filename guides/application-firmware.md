# Upgrade or downgrade application firmware

This feature concerns the firmware application component running inside a robot or station. It does not install an older version of the SwitchBot phone application. Bootloader replacement, OTP and fuse changes are outside the project scope.

An older image being available is not evidence that it can be installed safely. Each supported transition is a directed edge from an exact source configuration to an exact target configuration. The reverse direction needs its own qualification.

Before an operation is offered, its profile must establish:

- The physical model, hardware revision and component receiving the image.
- Source component versions, target versions and the exact image SHA-256 digest.
- Image format, integrity/authenticity checks, rollback/version rules and configuration compatibility.
- Entry, transfer, finalization, reconnect and installed-version verification behavior.
- The tested response to interruption and a practical recovery procedure.

There are currently no qualified OTA transitions in the release catalog. Development can parse images and exercise an offline transport simulator while hardware qualification remains incomplete.

The application shows the component, source and destination versions, expected disconnect/reboot and recovery steps before execution. An interrupted transfer is never displayed as successful merely because all bytes were queued for transmission.
