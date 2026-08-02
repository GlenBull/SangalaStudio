#!/usr/bin/env python3
"""Can a Mac talk to a Silhouette die cutter over libusb?

That is the ONE question this answers, and it is the question that gates a macOS port of Sangala
Studio. Everything else already runs on macOS: the browser UI is HTML and speaks only to localhost,
and the GPGL command layer is identical on every platform. What does not carry over is the USB
transport - on Windows the machine is opened through the usbprint.sys device interface, which has no
macOS equivalent. The cross-platform path is libusb, and inkscape-silhouette drives these same machines
on macOS through it, so this is expected to work. Expected is not measured.

The specific risk this is looking for: macOS has its own USB printing class driver, and a die cutter
enumerates as a USB printer. If that driver holds the interface, libusb cannot simply detach it the way
it can on Linux, and the port becomes considerably harder. The failure will show up below as a busy or
access error on claim, and that is the sentence worth sending back.

WHAT IT DOES TO THE MACHINE: almost nothing. It sends ESC EOT (initialize) and ESC ENQ (report status),
then reads one byte back. No motion, no blade, no cutting. Nothing is written to the machine that a
power cycle does not undo.

    python3 -m pip install pyusb
    brew install libusb
    python3 mac_usb_probe.py

Written for Moses. Send back everything it prints, including a failure - a failure names the obstacle.
"""
import sys

SILHOUETTE_VID = 0x0B4D
KNOWN = {                       # PID -> (name, cut width in mm)
    0x113A: ("Silhouette Portrait 3", 203),
    0x113F: ("Silhouette Portrait 4", 216),
    0x112B: ("Silhouette Cameo 2", 304),
}
INIT   = b"\x1b\x04"            # ESC EOT - initialize
STATUS = b"\x1b\x05"            # ESC ENQ - report status
STATUS_MEANING = {"0": "ready", "1": "moving", "2": "no media loaded"}


def main():
    try:
        import usb.core, usb.util
    except ImportError:
        print("pyusb is not installed.  Run:  python3 -m pip install pyusb")
        return 2

    print("Looking for a Silhouette die cutter (USB vendor 0x0B4D)...")
    devices = list(usb.core.find(find_all=True, idVendor=SILHOUETTE_VID))
    if not devices:
        print("  none found.")
        print("  Check the die cutter is powered on and connected by USB, not only by Bluetooth.")
        print("  If it is on and connected, libusb may not be able to see it at all - that is itself")
        print("  a useful answer, so send this output back.")
        return 1

    for dev in devices:
        pid = dev.idProduct
        name, width = KNOWN.get(pid, ("unrecognized model", None))
        print("\nFound: %s  (vendor 0x%04X, product 0x%04X)" % (name, dev.idVendor, pid))
        if width:
            print("  cut width %d mm" % width)
        else:
            print("  This product id is not in Sangala Studio's table; it would fall back to Portrait 3")
            print("  settings. Worth reporting either way.")
        try:
            print("  manufacturer: %s" % (dev.manufacturer or "?"))
            print("  product     : %s" % (dev.product or "?"))
        except Exception as e:                       # reading strings can itself need access
            print("  (could not read the descriptor strings: %s)" % e)

        probe(dev, usb)
    return 0


def probe(dev, usb):
    """Claim the interface, ask the machine for its status, and report exactly what happened."""
    import usb.util
    cfg = None
    try:
        dev.set_configuration()                      # harmless if already configured
        cfg = dev.get_active_configuration()
    except Exception as e:
        print("  COULD NOT CONFIGURE: %s" % e)
        print("  This is usually another driver holding the device.")
        return

    intf = cfg[(0, 0)]
    print("  interface class %d (7 = printer), %d endpoints"
          % (intf.bInterfaceClass, intf.bNumEndpoints))

    # macOS is the interesting case: is_kernel_driver_active is not implemented on every backend,
    # so ask, but do not let the question itself end the run.
    try:
        if dev.is_kernel_driver_active(intf.bInterfaceNumber):
            print("  a kernel driver currently holds this interface; trying to detach it")
            try:
                dev.detach_kernel_driver(intf.bInterfaceNumber)
                print("  detached")
            except Exception as e:
                print("  COULD NOT DETACH: %s" % e)
                print("  THIS IS THE ANSWER WE ARE LOOKING FOR - macOS's own printing class driver is")
                print("  holding the die cutter and will not let go. Send this line back.")
                return
    except NotImplementedError:
        print("  (this libusb backend cannot report whether a kernel driver is attached - normal on macOS)")
    except Exception as e:
        print("  (kernel-driver check failed: %s)" % e)

    try:
        usb.util.claim_interface(dev, intf.bInterfaceNumber)
        print("  claimed the interface")
    except Exception as e:
        print("  COULD NOT CLAIM: %s" % e)
        print("  If this says 'busy' or 'access denied', a system driver has the device. That is the")
        print("  obstacle the port has to solve, so this line is the important one.")
        return

    try:
        out = usb.util.find_descriptor(intf, custom_match=lambda e:
              usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        inp = usb.util.find_descriptor(intf, custom_match=lambda e:
              usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
        if out is None or inp is None:
            print("  could not find both a bulk OUT and a bulk IN endpoint")
            return
        print("  endpoints: OUT 0x%02X, IN 0x%02X" % (out.bEndpointAddress, inp.bEndpointAddress))

        out.write(INIT)                              # ESC EOT
        out.write(STATUS)                            # ESC ENQ
        reply = bytes(inp.read(64, timeout=3000)).decode("ascii", "replace").strip()
        meaning = STATUS_MEANING.get(reply[:1], "unrecognized")
        print("  STATUS REPLY: %r  (%s)" % (reply, meaning))
        print()
        print("  SUCCESS - a Mac can open this die cutter and hold a conversation with it.")
        print("  The USB transport is not an obstacle to porting Sangala Studio.")
    except Exception as e:
        print("  TALKING TO IT FAILED: %s" % e)
        print("  The interface was claimed, so the device is reachable; this is a protocol or")
        print("  endpoint problem rather than a permissions one. Send the message back as it is.")
    finally:
        try:
            usb.util.release_interface(dev, intf.bInterfaceNumber)
            usb.util.dispose_resources(dev)
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
