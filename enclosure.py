"""Parametric CadQuery models for the vacuum battery enclosure."""

from __future__ import annotations

import cadquery as cq

import config as cfg


def _rounded_box(length: float, width: float, height: float, radius: float) -> cq.Workplane:
    """Create a box centered on XY and sitting on the XY plane."""
    radius = max(0.0, min(radius, (min(length, width) / 2.0) - 0.01))
    return (
        cq.Workplane("XY")
        .rect(length - 2.0 * radius, width)
        .rect(length, width - 2.0 * radius)
        .vertices()
        .circle(radius)
        .extrude(height)
    )


def _magnet_positions() -> list[tuple[float, float]]:
    """Return the configured magnet pocket center points."""
    x = cfg.ENCLOSURE_LENGTH / 2.0 - cfg.MAGNET_EDGE_OFFSET_X
    y = cfg.ENCLOSURE_WIDTH / 2.0 - cfg.MAGNET_EDGE_OFFSET_Y
    return [(-x, -y), (-x, y), (x, -y), (x, y)]


def _battery_placeholder() -> cq.Workplane:
    """Create a visible placeholder volume for the future battery pack fit."""
    return (
        cq.Workplane("XY")
        .box(
            cfg.BATTERY_LENGTH + 2.0 * cfg.BATTERY_CLEARANCE,
            cfg.BATTERY_WIDTH + 2.0 * cfg.BATTERY_CLEARANCE,
            cfg.BATTERY_HEIGHT + 2.0 * cfg.BATTERY_CLEARANCE,
            centered=(True, True, False),
        )
        .translate((0, 0, cfg.WALL_THICKNESS + cfg.BATTERY_FLOOR_CLEARANCE))
    )


def make_base() -> cq.Workplane:
    """Build the lower enclosure shell with parametric placeholders."""
    outer = _rounded_box(
        cfg.ENCLOSURE_LENGTH,
        cfg.ENCLOSURE_WIDTH,
        cfg.BASE_HEIGHT,
        cfg.CORNER_RADIUS,
    )
    inner = _rounded_box(
        cfg.ENCLOSURE_LENGTH - 2.0 * cfg.WALL_THICKNESS,
        cfg.ENCLOSURE_WIDTH - 2.0 * cfg.WALL_THICKNESS,
        cfg.BASE_HEIGHT,
        max(0.0, cfg.CORNER_RADIUS - cfg.WALL_THICKNESS),
    ).translate((0, 0, cfg.WALL_THICKNESS))

    base = outer.cut(inner)

    # Lid registration rabbet near the top lip.
    rabbet = _rounded_box(
        cfg.ENCLOSURE_LENGTH - 2.0 * cfg.WALL_THICKNESS,
        cfg.ENCLOSURE_WIDTH - 2.0 * cfg.WALL_THICKNESS,
        cfg.LID_OVERLAP_DEPTH,
        max(0.0, cfg.CORNER_RADIUS - cfg.WALL_THICKNESS),
    ).translate((0, 0, cfg.BASE_HEIGHT - cfg.LID_OVERLAP_DEPTH))
    base = base.cut(rabbet)

    # Magnet pockets in the base lip.
    for x, y in _magnet_positions():
        pocket = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(cfg.MAGNET_DIAMETER / 2.0 + cfg.DEFAULT_CLEARANCE)
            .extrude(cfg.MAGNET_DEPTH)
            .translate((0, 0, cfg.BASE_HEIGHT - cfg.MAGNET_DEPTH))
        )
        base = base.cut(pocket)

    # Non-fitting placeholders for future component planning.
    base = base.union(_battery_placeholder())
    wire_channel = (
        cq.Workplane("XY")
        .box(
            cfg.WIRE_CHANNEL_LENGTH,
            cfg.WIRE_CHANNEL_WIDTH,
            cfg.WIRE_CHANNEL_DEPTH,
            centered=(True, True, False),
        )
        .translate((cfg.WIRE_CHANNEL_CENTER_X, cfg.WIRE_CHANNEL_CENTER_Y, cfg.WALL_THICKNESS))
    )
    usb_board = (
        cq.Workplane("XY")
        .box(
            cfg.USB_BOARD_LENGTH,
            cfg.USB_BOARD_WIDTH,
            cfg.USB_BOARD_HEIGHT,
            centered=(True, True, False),
        )
        .translate((cfg.USB_BOARD_CENTER_X, cfg.USB_BOARD_CENTER_Y, cfg.USB_BOARD_Z))
    )
    base = base.union(wire_channel).union(usb_board)

    # Side-wall connector opening placeholders.
    usb_cut = (
        cq.Workplane("XZ")
        .center(cfg.USB_BOARD_CENTER_X, cfg.USB_BOARD_Z + cfg.USB_PORT_HEIGHT / 2.0)
        .rect(cfg.USB_PORT_WIDTH, cfg.USB_PORT_HEIGHT)
        .extrude(cfg.WALL_THICKNESS * 3.0)
        .translate((0, -cfg.ENCLOSURE_WIDTH / 2.0 - cfg.WALL_THICKNESS, 0))
    )
    dc_cut = (
        cq.Workplane("XZ")
        .center(cfg.DC_JACK_CENTER_X, cfg.DC_JACK_CENTER_Z)
        .circle(cfg.DC_JACK_DIAMETER / 2.0 + cfg.DEFAULT_CLEARANCE)
        .extrude(cfg.WALL_THICKNESS * 3.0)
        .translate((0, -cfg.ENCLOSURE_WIDTH / 2.0 - cfg.WALL_THICKNESS, 0))
    )
    return base.cut(usb_cut).cut(dc_cut)


def make_lid() -> cq.Workplane:
    """Build the magnet-retained lid with placeholder controls and indicators."""
    lid = _rounded_box(
        cfg.ENCLOSURE_LENGTH,
        cfg.ENCLOSURE_WIDTH,
        cfg.LID_HEIGHT,
        cfg.CORNER_RADIUS,
    )

    underside_relief = _rounded_box(
        cfg.ENCLOSURE_LENGTH - 2.0 * cfg.WALL_THICKNESS,
        cfg.ENCLOSURE_WIDTH - 2.0 * cfg.WALL_THICKNESS,
        cfg.LID_HEIGHT,
        max(0.0, cfg.CORNER_RADIUS - cfg.WALL_THICKNESS),
    ).translate((0, 0, cfg.LID_TOP_THICKNESS))
    lid = lid.cut(underside_relief)

    lip = _rounded_box(
        cfg.ENCLOSURE_LENGTH - 2.0 * (cfg.WALL_THICKNESS + cfg.LID_FIT_CLEARANCE),
        cfg.ENCLOSURE_WIDTH - 2.0 * (cfg.WALL_THICKNESS + cfg.LID_FIT_CLEARANCE),
        cfg.LID_OVERLAP_DEPTH,
        max(0.0, cfg.CORNER_RADIUS - cfg.WALL_THICKNESS - cfg.LID_FIT_CLEARANCE),
    )
    lid = lid.union(lip)

    for x, y in _magnet_positions():
        pocket = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(cfg.MAGNET_DIAMETER / 2.0 + cfg.DEFAULT_CLEARANCE)
            .extrude(cfg.MAGNET_DEPTH)
            .translate((0, 0, 0))
        )
        lid = lid.cut(pocket)

    first_led_x = cfg.LED_WINDOW_CENTER_X - (cfg.LED_WINDOW_COUNT - 1) * cfg.LED_WINDOW_SPACING / 2.0
    for index in range(cfg.LED_WINDOW_COUNT):
        led_cut = (
            cq.Workplane("XY")
            .center(first_led_x + index * cfg.LED_WINDOW_SPACING, cfg.LED_WINDOW_CENTER_Y)
            .circle(cfg.LED_WINDOW_DIAMETER / 2.0 + cfg.DEFAULT_CLEARANCE)
            .extrude(cfg.LID_HEIGHT * 2.0)
            .translate((0, 0, -cfg.LID_HEIGHT / 2.0))
        )
        lid = lid.cut(led_cut)

    button_cut = (
        cq.Workplane("XY")
        .center(cfg.PUSH_BUTTON_CENTER_X, cfg.PUSH_BUTTON_CENTER_Y)
        .circle(cfg.PUSH_BUTTON_DIAMETER / 2.0 + cfg.DEFAULT_CLEARANCE)
        .extrude(cfg.LID_HEIGHT * 2.0)
        .translate((0, 0, -cfg.LID_HEIGHT / 2.0))
    )
    return lid.cut(button_cut)


__all__ = ["make_base", "make_lid"]
