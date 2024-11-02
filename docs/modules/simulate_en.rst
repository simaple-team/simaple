************************************
About Simulation: An Explanation
************************************

.. contents:: Contents
    :local:


Introduction
============

The ultimate goal of simaple is to be a perfect simulator of an in-game environment. 
This is a very difficult goal to achieve, since the underlying mechanisms of skills in the game are much more complicated than one can deduce by the naked eye. 
Attempting to model it with simplifications as in the past will lead to uncontrollable inter-module dependencies and errors which can't be tested for.  

The ``simulate`` module is a library that uses Redux Pattern to describe these complex interactions between skills.


Why Redux?
===========

The ``simulate`` module uses Redux Pattern to define the entire system and perform the simulation.

To start with, let's think a bit about Skills in MapleStory. Skills normally have states; being on cooldown, for example, is a state. 
Performing skill-related actions can change these states; using a skill results in that skill's effects occurring, and then that skill goes on cooldown. 
As time passes, the remaining cooldown decreases. Some skills, like Pathfinder's Ancient Force skills, have their states change by interacting with other skills.

This can be modelled by an "action-state" relationship. The keys we press and skills we use, correspond to Actions, and the state of each skill can be stored in States.
If each skill has a state, and these states change frequently, we can store these states in a ``Store`` and try using Redux Pattern.

All states are stored in the Store, and can be changed by a Dispatcher.
simaple considers a skill to be a collection of methods that change states. The ``Component`` class is used to express this.
A Component is a collection of Dispatchers that can be referred to together as one object. This can correspond to one skill object in the game.

All interactions are defined in states.
For example, consider the case where Skill A changes the cooldown of Skill B. In this case, the action is the use of Skill A, but what actually changes is the state of Skill B. 
Therefore, this trigger will be defined in the state description of Skill B.
This might seem unintuitive at first; it is more natural to see interactions like this as the results of Skill A, rather than defined in the states of the other states they affect. 
However, this model results in a single action changing multiple states through multiple sequences.
We adhere to the following principle:

``All state changes caused by one action will occur at once``

The logic flow by which one action causes multiple state changes in sequence makes it difficult to understand the system from the "Player" perspective of controlling the system. 
"Players" are normally unable to predict what side-effects their actions can have. 
All in-system action processing must be limited to single action processing and the reinterpretation of Event into Action must be controlled by the "Player".

Definitions
===============

Action
-------
Any user behaviour corresponds to an Action. Simulations begin with the user creating and delivering an Action.
Actions correspond to commands given to the character in-game. The Action is to either press a specific skill, or to wait for a specific time without any input.
Actions have the properties ``name``, ``method``, ``payload``. 

Event
-------

An ``Event`` is the result of an ``Action``. 
By and large, Events can be divided into things that require processing like action delays and damage dealt, and events that guide the execution of certain skills for logging purposes. 
Other than delay events which progress the time of the entire system, events do not necessarily need to be processed.
The "Elapsed time" event is the only event that requires processing; this is to allow the Player to apply different delays than the normal expected skill delays, e.g. during skill animation cancellation.

State
-------
``State`` refers to the state of the skills of the simulated character. In general, an ``Action`` changes a ``State``, then may cause one or more ``Event`` (or none).
A ``State`` should contain all the information needed to be changed by any ``Action``. At the same time, no state will be modelled by any method other than ``State`` that can be modified by any ``Action``.

Entity
-------
simaple defines a ``State`` to be a set of ``Entity``. An ``Entity`` is the smallest unit of a state that has its own characteristics. 
For example, a typical buff skill has a duration and a cooldown. Each of these can be modelled in code as ``Cooldown`` and ``Duration`` entities.

The ``State`` of this buff skill can be defined as follows:

.. code-block:: python
    
    class Cooldown(Entity):
        ...

    class Duration(Entity):
        ...

    class BuffSkillState(State):
        cooldown: Cooldown
        duration: Duration



Store
-------

The ``Store`` is the space that stores all ``State`` in a system. It is the single source of truth of the system, and all states must be obtainable from the ``Store``.

Dispatcher
------------

A ``Dispatcher`` is a description of a method of change a state. From the definition described above, any state-changing behaviour will have the following signature; this is called a Dispatcher.

``(Store, Action) -> (Event)``

Paying attention to the signature, the Dispatcher does not simply change a state, but it changes the ``Store`` received as a parameter. 
Because of this, Dispatchers do not guarantee immutability of States in the Store, and hence are not pure functions.

Reducer
----------

A Dispatcher is not a suitable interface for developers because it is not a pure function. 
Therefore, simaple provides a pure function interface called a ``Reducer`` to help developers write intuitive and sustainable code.
A ``Reducer`` is a function that has the following signature:

``(Any, State) -> (State, list[Event])``

A Reducer is a pure function because the ``State`` given to it is unchanged.
Internally, a Reducer is implemented as being wrapped by a Dispatcher via the ``ReducerMethodWrappingDispatcher``, which returns a changed State.

A Reducer is a pure function, but its definition is complicated. 
This complexity is necessary for simaple to support many state-change systems.
However, from a developer's point of view, it is inconvenient and difficult to create a Reducer while following the above rules.
So, to simplify things, Components can be used to easily create Reducers, and these can be wrapped in Dispatchers.

Component
----------

Components are the core of simaple's simulation procedure. ``Component`` instance methods are easily converted into Reducers via the ``@reducer_method`` decorator.

Let's look at a simple example:

.. code-block:: python

    ## 1. Define State
    class AttackSkillState(ReducerState):
        cooldown: Cooldown
        dynamics: Dynamics

    class AttackSkillComponent(Component, InvalidatableCooldownTrait, UseSimpleAttackTrait):
        ## 2. Define constructor
        name: str
        damage: float
        hit: float
        cooldown: float = 0.0
        delay: float

        ## 3. Define state initializer
        def get_default_state(self):
            return {
                "cooldown": Cooldown(time_left=0),
            }

        ## 4. A reducer
        @reducer_method
        def elapse(self, time: float, state: AttackSkillState) -> tuple[AttackSkillComponent, list[Event]]:
            return self.elapse_simple_attack(time, state)

        @reducer_method
        def use(self, _: None, state: AttackSkillState) -> tuple[AttackSkillComponent, list[Event]]:
            return self.use_simple_attack(state)

        def _get_simple_damage_hit(self) -> tuple[float, float]:
            return self.damage, self.hit


A Component consists of four main parts.

Firstly, we declare the State that the Component will use. This State definition will be used to define the Reducer for the Component.

Secondly, we define the constructor for the Component. 
Since Components inherit ``pydantic.BaseModel``, they use the ``pydantic.BaseModel`` constructor definition style to specify the data types needed for the Component to be defined.
Refer to the documentation in ``pydantic.BaseModel`` for more information.

Thirdly, we define a default state via ``get_default_state``.
All Components must define a method to specify and deliver an initial value when an Entity required for one of the Component's Reducers is missing.
Some Entities have default values defined elsewhere; for example, ``dynamics`` is defined in ``global_property.py``.
The keys used here must match the variable names in the previously declared ``AttackSkillState``, or else the program will not be able to recognise which Entity the default value provided corresponds to.

Finally, methods decorated with ``@reducer_method`` are defined.
Note the signature of this function; these are the Reducers we have been looking for.
The ``elapse`` method takes ``state: AttackSkillState`` as its second parameter.
This signature specifies that the value passed should be specifically an ``AttackSkillState``-typed object within the Store.
Based on this signature, the internal implementation will query the Store appropriately and return the appropriate State combination.

This code allows a Component to be well defined by bringing together the actions associated with certain states.
This corresponds to one **skill** in the game. That is, we manage skill objects readably and maintainably through ``Component``.
A helpful thing to keep in mind is that the State of the skill and the Reducers associated with it are strongly connected.


Component Links
----------------------

Sometimes, skills interact with other skills. They will need to either trigger their own events or change their state when other skills are used.
simaple supports the ``binds`` property so that the Component can directly access the state of other Components.
The states specified in ``binds`` will query the Store for the state value of the corresponding key when the Reducer is called and assign a specified value to it.

.. code-block:: python

    component = AttackSkillComponent(
        name="Absolute Kill",
        binds={
            ".Baptism of Light and Darkness.stack_state": "baptism_of_light_and_darkness_stack_state"
        }
    )
    ...
    class AbsoluteKillComponent(AttackSkillComponent):
        ...
        @reducer_method
        def use(self, _, cooltime_state, baptism_of_light_and_darkness_stack_state):
            ...
