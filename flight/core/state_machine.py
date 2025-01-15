import core.scheduler as scheduler
from core import logger
from core.states import STATES


class StateManager:
    """Singleton Class"""

    _instance = None

    __slots__ = (
        "__current_state",
        "__scheduled_tasks",
        "__initialized",
        "__config",
        "__states",
        "__tasks",
        "__previous_state",
    )

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):

        self.__current_state = None
        self.__scheduled_tasks = {}
        self.__initialized = False
        self.__config = None

    @property
    def current_state(self):
        return self.__current_state

    @property
    def scheduled_tasks(self):
        return self.__scheduled_tasks

    def start(self, start_state=STATES.STARTUP):
        """Starts the state machine

        Args:
        :param start_state: The state to start the state machine in
        :type start_state: STATES
        """
        from core.sm_configuration import SM_CONFIGURATION

        self.__config = SM_CONFIGURATION

        # TODO Validate the configuration and registry
        self.__states = list(self.__config.keys())

        # init task objects
        from core.sm_configuration import TASK_REGISTRY

        self.__tasks = {id: task(id) for id, task in TASK_REGISTRY.items()}

        self.__current_state = start_state

        # Will load all the tasks through the state switch
        self.switch_to(start_state)
        scheduler.run()

    def switch_to(self, new_state_id: int):
        """Switches to a new state and actiavte all corresponding tasks as defined in the SM_CONFIGURATION

        Args:
        :param new_state: The name of the state to switch to
        :type new_state_id: id
        """

        if new_state_id not in self.__states:
            logger.critical(f"State {new_state_id} is not in the list of states")
            raise ValueError(f"State {new_state_id} is not in the list of states")

        if self.__initialized:
            # prevent illegal transitions
            if not (new_state_id in self.__config[self.__current_state]["MovesTo"]):
                logger.critical(f"No transition from {self.__current_state} to {new_state_id}")
                raise ValueError(f"No transition from {self.__current_state} to {new_state_id}")
        else:
            self.__initialized = True

        self.__previous_state = self.__current_state

        self.stop_all_tasks()
        self.schedule_new_state_tasks(new_state_id)

        logger.info(f"Switched to state {new_state_id}")

    def stop_all_tasks(self):
        for name, task in self.__scheduled_tasks.items():
            task.stop()

    def schedule_new_state_tasks(self, new_state):

        self.__scheduled_tasks = {}  # Reset
        self.__current_state = new_state
        state_config = self.__config[new_state]

        for task_id, props in state_config["Tasks"].items():

            if "ScheduleLater" in props:
                schedule = scheduler.schedule_later
            else:
                schedule = scheduler.schedule

            frequency = props["Frequency"]
            priority = props["Priority"]
            task_fn = self.__tasks[task_id]._run
            self.__tasks[task_id].set_frequency(frequency)

            self.__scheduled_tasks[task_id] = schedule(frequency, task_fn, priority)

    def query_task_states(self):
        state = {}
        for task in self.__scheduled_tasks:
            state[task] = task.query_state()
        return state

    def print_current_tasks(self):
        """Prints all current tasks being executed"""
        for task_name in self.__scheduled_tasks:
            print(task_name)

    def change_task_frequency(self, task_id, freq_hz):
        """Changes the frequency of a task"""
        self.__scheduled_tasks[task_id].change_rate(freq_hz)
        logger.info(f"Task {task_id} frequency changed to {freq_hz}")
        # TODO - change the persistent sm_configuration
