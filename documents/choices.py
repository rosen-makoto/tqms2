DESIGN_OWNERSHIP_CHOICES = [
    ("SELF", "We own the design."),
    ("ELSE", "Design is owned by someone else."),
]

MANUFACTURING_OPTIONS_CHOICES = [
    ("SELF", "Only we manufacture this part."),
    ("ELSE", "We source this part externally."),
    ("BOTH", "Both we and someone else are able to manufacture this part."),
]

FINISHED_DEVICE_CHOICES = [
    ("NO", "This is not a finished device."),
    ("NONSHIPPABLE", "This is or contains finished device(s), but is not yet shippable."),
    ("SHIPPABLE", "This is or contains finished device(s) and is shippable."),
]