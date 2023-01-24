*****************************
simaple: Tutorial (English)
*****************************

.. contents:: Contents
    :local:


Introduction
==============

**simaple** is a tool that can be used to define skills and using these defined skills to perform simulations. The goal is to create a perfect simulation of in-game skill usage.

In this tutorial, we will be creating a simulation of an ``Archmage (Fire/Poison)``. Based on this tutorial, any job can be recreated in a similar way.

For more advanced features, see the Advanced Features Guide.

Start
========

To implement the simulation, we first need to define a set of skills to be used. 
The results of using each skill will then be interpreted by converting it into damage based on the stats of the target character.


Defining Skillsets
===================

In simaple, a collection of skills available to be used is called a Client. Clients can be created using the ``get_client`` method.

.. code-block:: python

    from simaple.simulate.kms import get_client
    from simaple.data.client_configuration import get_client_configuration
    from simaple.core.jobtype import JobType
    from simaple.core import ActionStat, Stat

    client_configuration = get_client_configuration(JobType.archmagefb)
    character_stat = Stat(
        INT=4932.0,
        INT_multiplier=573.0,
        INT_static=15460.0,
        magic_attack=2075.0,
        magic_attack_multiplier=81.0,
        critical_rate=100.0,
        critical_damage=83.0,
        boss_damage_multiplier=144.0,
        damage_multiplier=167.7,
        final_damage_multiplier=110.0,
        ignored_defence=95,
    )
        
    action_stat = ActionStat(buff_duration=185)

    client = get_client(
        action_stat,
        client_configuration.get_groups(),
        {
            "character_stat": character_stat,
            "character_level": 260,
            "weapon_attack_power": 789,
            "weapon_pure_attack_power": 500,
        },
        client_configuration.get_filled_v_skill(30),
        client_configuration.get_filled_v_improvements(60),
        combat_orders_level=1,
        passive_skill_level=0,
    )


The above code is pretty long! However, all parameters are required to define a Client. 
Let's focus on a few important elements that we need to know about first.

- ``get_client_configuration`` will load pre-defined job configurations as ``client_configuration`` objects. These objects will handle the complex tasks related to the job of interest. 
- ``ActionStat`` and ``Stat`` represent the stats used to perform the simulation. ``character_stat`` represents the stats of the character, while ``ActionStat`` is an object that contains information such as Buff Duration and Summon Duration. In the above code, buff duration is set to 185%.

- The 3rd parameter of ``get_client`` is slightly more complicated and specifies a dict of background information required to make the simulation work. The following parameters are required:

  - ``character_stat``: This is the ``Stat`` object previously defined, which is the simulating character's stats.
  - ``character_level`` : Level of the character (used for level difference damage bonus/penalty calculations and Maple Warrior/AP related calculations).
  - ``weapon_attack_power`` : Total Weapon Attack / Magic Attack (where relevant) value of the weapon used (including flames, stars and scrolling).
  - ``weapon_pure_attack_power`` : Base Weapon Attack / Magic Attack value of the weapon (just the white number on the weapon).

- The 4th parameter of ``get_client`` specifies the levels used for the 5th job skills. It's troublesome to do this manually, but the ``client_configuration`` object earlier allows us to conveniently create a default configuration of all skills at Level 30.
- Similarly, the 5th parameter specifies the levels of Enhancement Cores. ``client_configuration.get_filled_v_improvements(60)`` specifies an assumption that all skills are enhanced to level 60.
- ``combat_orders_level`` is the level of Combat Orders used (1 = Decent, 2 = Paladin), and ``passive_skill_level`` is either 0 or 1 depending on whether the "+1 Levels to Passive Skills" Legendary Ability line is used.

With all the information provided, ``get_client`` returns a ``Client`` object which, in the above code, is referenced as ``client``. 

Congratulations! We have now created a ``Client`` with all the skills necessary.


Actor Implementation
==============

In the previous section, we have created the *environment* for the desired simulation. In this section, we will discuss how to actually **simulate** skill usage given this environment.

In simaple, ``Actor`` is the class for defining decisions such as which skill to use in which sequence. For a predefined Actor that works simply for all jobs, simaple offers ``MDCActor``. Let's create it with ``client_configuration``. 

.. code-block:: python

    ...

    client_configuration = get_client_configuration(JobType.archmagefb)
    actor = client_configuration.get_mdc_actor()


Now we have both the ``Client`` and the ``Actor``. Next is to actually perform the simulation.


Performing the Simulation
===========================

The following code runs the simulation through the ``Client`` and ``Actor`` defined earlier. Let's run a simulation for 50 seconds; keep in mind that this code follows from the previous blocks.


.. code-block:: python

    ...

    events = []
    while client.environment.show("clock") < 50_000:
        action = actor.decide(client.environment, events)
        events = client.play(action)

The total time for which the simulation has been run can be obtained from ``client.environment.show("clock")``. For the duration of the simulation, we take the decision of the ``Actor``, perform it in the ``Client``, and then the resulting list of ``events`` is passed to the next decision.

The simulation has run, but at the moment the results aren't displayed yet. simaple has methods to track the following two results for analysis.    

- The sequence of decisions made by the ``Actor`` at each point in time (Record)
- The damage amount caused by the ``Actor``'s decision (Report)

If we run the code below *instead of* the one above, we can store these two things to be viewed after the simulation is run.


.. code-block:: python

    ...

    from simaple.simulate.actor import ActionRecorder
    from simaple.simulate.report.base import Report, ReportEventHandler

    recorder = ActionRecorder("record.tsv")
    report = Report()
    client.add_handler(ReportEventHandler(report))

    events = []
    with recorder.start() as rec:
        while client.environment.show("clock") < 50_000:
            action = actor.decide(client.environment, events)
            events = client.play(action)
            rec.write(action, client.environment.show("clock"))
    
    report.save("report.tsv")

    


``recorder`` records the ``Actor``'s decisions at each instant in time. Every action taken, ``rec.write`` is called to record the decisions made.
The record will be stored in ``record.tsv`` after the code has been executed. Parsing the information there might be a bit hard since it's pretty raw data, but it would describe the names of the skills used and the time (in the simulation) at which they were used.

``report`` contains information about the damage numbers that occurred at each instant. By calling ``add_handler`` to register  ``report`` with the ``Client``, all the damage that occurred during the simulation process is stored in the ``report`` object.
``len(report)`` can be used to verify if the ``Report`` has actually piled up. You can also change the simulation duration and rerun the code to see that the length actually changes.  

The ``report.save`` method can be used to output the report as a file.


Damage calculations
=========================

We have performed a simulation, and obtained results. All that's left is to process them in a way that allows tractable analysis. Processing allows statistics analysis, graphing, and calculating DPM.
simaple does not store any actual outputted damage numbers in the log by default. To replace the damage log with actual damage numbers, a ``DamageCalculator`` needs to be declared.


.. code-block:: python

    ...

    from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage
    from simaple.data.damage_logic import get_damage_logic

    damage_calculator = DamageCalculator(
        character_spec=character_stat,
        damage_logic=get_damage_logic(JobType.archmagefb, combat_orders_level=1),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
    )


Quite a bit of information really is required to actually calculate the damage output. 
First of all, the character stat information (``character_stat``) is required.
``damage_logic`` specifies the damage calculation method. 
Call the ``get_damage_logic`` function to retrieve the respective damage calculation logic for the job. 
Specifying ``JobType.archmagefb`` and ``combat_orders_level=1`` specifies that the main stat is INT, Magic Attack is used, the secondary stat is LUK, and that the weapon constant used is 1.2, and that Decent Combat Orders is used. 
``armor=300`` specifies the DEF of the target.
``level_advantage`` and ``force_advantage`` specifies the final damage multipliers resulting from level differences and Arcane/Authentic Force differences, respectively. The Level Advantage is inconvenient to calculate, so calling ``LevelAdvantage`` is recommended.


And for the finishing touch, let's actually calculate dpm with the ``damage_calculator`` configured. Calculation is instant.

.. code-block:: python

    ...

    print(f"{damage_calculator.calculate_dpm(report):,}")

The above outputs the calculated dpm.


Finally, this will be the full code assembled from all the sections written above.

.. code-block:: python

    from simaple.simulate.kms import get_client
    from simaple.data.client_configuration import get_client_configuration
    from simaple.core.jobtype import JobType
    from simaple.core import ActionStat, Stat

    ## Declare Client
    client_configuration = get_client_configuration(JobType.archmagefb)
    character_stat = Stat(INT=50000, final_damage_multiplier=50)
    action_stat = ActionStat(buff_duration=185)

    client = get_client(
        action_stat,
        client_configuration.get_groups(),
        {
            "character_stat": character_stat,
            "character_level": 260,
            "weapon_attack_power": 789,
            "weapon_pure_attack_power": 500,
        },
        client_configuration.get_filled_v_skill(30),
        client_configuration.get_filled_v_improvements(60),
        combat_orders_level=1,
        passive_skill_level=0,
    )

    ## Declare Actor

    client_configuration = get_client_configuration(JobType.archmagefb)
    actor = client_configuration.get_mdc_actor()

    ## Run simulation

    from simaple.simulate.actor import ActionRecorder
    from simaple.simulate.report.base import Report, ReportEventHandler

    recorder = ActionRecorder("record.tsv")
    report = Report()
    client.add_handler(ReportEventHandler(report))

    events = []
    with recorder.start() as rec:
        while client.environment.show("clock") < 50_000:
            action = actor.decide(client.environment, events)
            events = client.play(action)
            rec.write(action, client.environment.show("clock"))

    from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage
    from simaple.data.damage_logic import get_damage_logic

    ## Calculate DPM

    damage_calculator = DamageCalculator(
        character_spec=character_stat,
        damage_logic=get_damage_logic(JobType.archmagefb, combat_orders_level=1),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
    )

    print(f"{damage_calculator.calculate_dpm(report):,}") # Our simulation's DPM
