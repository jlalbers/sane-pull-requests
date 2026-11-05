Precise raster edit, performed with Pillow and NumPy; no image generation.

Base: the user-provided Gemini-generated banner, 3584 x 1184 pixels.
Copied the original viewer-left C claw to the viewer-right wrist by translating
its pixels 358 pixels right and 32 pixels up. No scaling or redrawing of the claw.
Removed the oversized right claw and restored the packet border it covered.
Saved as lossless PNG to retain unchanged decoded source pixels.

Verified: original left claw unchanged; copied claw pixels identical to their
source; all changes confined to the right claw and adjacent packet-border repair.
Independent visual review passed for matching shape, wrist, border and remnants.
