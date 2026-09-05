# Device families and current scope

Names identify research subjects, not interchangeable hardware. The corpus inventory groups identical bytes by SHA-256 and records filename aliases separately.

| Family | Roles under investigation | Current boundary |
| --- | --- | --- |
| K10+ / `WoSweeperMini` | Robot, barrel | First application target; recovered protocol claims are being revalidated against exact images |
| K10+ Pro | Robot, Pro barrel | Explicit per-image deltas required; similar names do not establish equivalence |
| S10 / `WoSweeperOrigin` | Robot, water station, dust/charging station and radio components | Distinguish main and remote controllers; persistent station names are not yet a demonstrated operation |
| K11 | Robot and stations when attributed | No confidently attributed robot firmware baseline established in this inventory |
| Internally named K20 / opaque mirror IDs | Robot, charge station, handheld and remote components | Directory/filename labels do not establish a particular marketed K20 product or physical compatibility |

Cross-family pairing requires separate mechanical and electrical evidence. In particular, the manufacturer states that K20+ Pro and K10+ Pro Combo Dual Empty Station hardware must not be interchanged because of different internal power outputs. This restriction does not classify every ordinary K10/K11 combination. [Manufacturer compatibility note](https://support.switch-bot.com/hc/en-us/articles/34362589597335-Can-the-Robot-K20-Pro-Be-Docked-and-Used-with-the-Dual-Empty-Station-of-SwitchBot-Robot-Vacuum-K10-Pro-Combo).

For every selected firmware baseline, the branch inventory will classify each relevant dispatcher branch as implemented, rejected, stub, internal or unresolved. Static coverage and hardware qualification are reported independently.
