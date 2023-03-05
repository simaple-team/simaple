[![kr](https://img.shields.io/badge/lang-kr-red.svg)](README.md)

# simaple: Simulation library for Maplestory

`simaple` is a library to analyse the combat environment in MapleStory.

simaple uses client resources to construct a simulation environment for MapleStory jobs with appropriate combat scenarios to calculate the expected DPM and relative DPM-share of each skill.

- Provides a realistic simulation environment based on actual game parameters in MapleStory
- Generates and analyses battle results including the expected DPM of the character with given specifications
- Provides a simulation environment based on in-game user information
- Calculates multi-faceted metrics to describe character spec level, such as converted stat (via the popular KMS Stat Conversion sheet)


## Web Client

simaple also provides a web interface to factilitate simulation.

![image](https://user-images.githubusercontent.com/39217532/222165238-00926269-e581-4cd6-8e4c-aef5cff8e4ce.gif)
- The web client can be installed at [simaple/web](https://github.com/simaple-team/web).


## Install

- `pip install simaple`

## Documentation

- https://simaple.readthedocs.io/en/latest/


### Community

- [Discord](https://discord.gg/5hgN5EbyA4)
- [Slack](https://join.slack.com/t/maplestorydpmcalc/shared_invite/zt-1lwi3l97o-EH0R9~W97SB8TjsoXnpzpQ)


## Developments & Contribution

- See [CONTRIBUTING](CONTRIBUTING.md)

## Supported Features

### In-game simulation
- Create an interactive simulation environment
  - Create a simulation environment with all variables present in-game, such as reduced / skipped cooldowns, increased buff duration, and V-matrix enhancements
- Real-time analyses of simulation results
  - DPM calculation
  - Relative dpm-share of each skill
  - Output results in a human-readable format for more thorough analysis

### Equipment related
- Calculate expected performance of equipment when applying specified Star Force and Scroll upgrades
- Via GearBlueprint, performance calculation of standardised reference character specs used in converted-stat calculations, etc.
- Calculate converted-stat, stat efficiencies and equivalences

### Linking to KMS Homepage
- Ability to load characters (who have agreed to disclose their information) from the KMS Homepage as a simple object
