#!/usr/bin/env python3

import re
from collections import Counter

import sys
print(sys.version)

class ChatBot:
    """A tag-based chatbot framework
    This class is not meant to be instantiated. Instead, it provides helper
    functions that subclasses could use to create a tag-based chatbot. There
    are two main components to a chatbot:
    * A set of STATES to determine the context of a message.
    * A set of TAGS that match on words in the message.
    Subclasses must implement two methods for every state (except the
    default): the `on_enter_*` method and the `respond_from_*` method. For
    example, if there is a state called "confirm_delete", there should be two
    methods `on_enter_confirm_delete` and `respond_from_confirm_delete`.
    * `on_enter_*()` is what the chatbot should say when it enters a state.
        This method takes no arguments, and returns a string that is the
        chatbot's response. For example, a bot might enter the "confirm_delete"
        state after a message to delete a reservation, and the
        `on_enter_confirm_delete` might return "Are you sure you want to
        delete?".
    * `respond_from_*()` determines which state the chatbot should enter next.
        It takes two arguments: a string `message`, and a dictionary `tags`
        which counts the number of times each tag appears in the message. This
        function should always return with calls to either `go_to_state` or
        `finish`.
    The `go_to_state` method automatically calls the related `on_enter_*`
    method before setting the state of the chatbot. The `finish` function calls
    a `finish_*` function before setting the state of the chatbot to the
    default state.
    The TAGS class variable is a dictionary whose keys are words/phrases and
    whose values are (list of) tags for that word/phrase. If the words/phrases
    match a message, these tags are provided to the `respond_from_*` methods.
    """

    STATES = []
    TAGS = {}

    def __init__(self, default_state):
        """Initialize a Chatbot.
        Arguments:
            default_state (str): The starting state of the agent.
        """
        if default_state not in self.STATES:
            print(' '.join([
                'WARNING:',
                'The default state ' + str(default_state) + ' is listed as a state.',
                'Perhaps you mean ' + str(self.STATES[0]) + '?',
            ]))
        self.default_state = default_state
        self.state = self.default_state
        self.tags = {}
        self._check_states()
        self._check_tags()

    def _check_states(self):
        """Check the STATES to make sure that relevant functions are defined."""
        for state in self.STATES:
            prefixes = []
            if state != self.default_state:
                prefixes.append('on_enter')
            prefixes.append('respond_from')
            for prefix in prefixes:
                if not hasattr(self, prefix + '_' + state):
                    print(' '.join([
                        'WARNING:',
                        'State "' + str(state) + '" is defined',
                        'but has no response function self.' + str(prefix) + '_' + str(state),
                    ]))

    def _check_tags(self):
        """Check the TAGS to make sure that it has the correct format."""
        for phrase in self.TAGS:
            tags = self.TAGS[phrase]
            if isinstance(tags, str):
                self.TAGS[phrase] = [tags]
            tags = self.TAGS[phrase]
            assert isinstance(tags, (tuple, list)), ' '.join([
                'ERROR:',
                'Expected tags for {phrase} to be str or List[str]',
                'but got ' + tags.__class__.__name__,
            ])

    def go_to_state(self, state):
        """Set the chatbot's state after responding appropriately.
        Arguments:
            state (str): The state to go to.
        Returns:
            str: The response of the chatbot.
        """
        assert state in self.STATES, 'ERROR: state "' + str(state) + ' is not defined'
        assert state != self.default_state, ' '.join([
            'WARNING:',
            "do not call `go_to_state` on the default state " + self.default_state + ";",
            'use `finish` instead',
        ])
        on_enter_method = getattr(self, 'on_enter_' + state)
        response = on_enter_method()
        self.state = state
        return response

    def chat(self):
        """Start a chat with the chatbot."""
        try:
            message = input('> ')
            while message.lower() not in ('exit', 'quit'):
                print()
                response = self.respond(message)
                if response is None:
                    print('WARNING: response from state ' + self.state + ' returned None')
                print(self.__class__.__name__ + ': ' + str(response))
                print()
                message = input('> ')
        except (EOFError, KeyboardInterrupt):
            print()
            exit()

    def respond(self, message):
        """Respond to a message.
        Arguments:
            message (str): The message from the user.
        Returns:
            str: The response of the chatbot.
        """
        respond_method = getattr(self, 'respond_from_' + self.state)
        return respond_method(message, self._get_tags(message))

    def finish(self, manner):
        """Set the chatbot back to the default state
        This function will call the appropriate `finish_*` method.
        Arguments:
            manner (str): The type of exit from the flow.
        Returns:
            str: The response of the chatbot.
        """
        response = getattr(self, 'finish_' + manner)()
        self.state = self.default_state
        return response

    def _get_tags(self, message):
        """Find all tagged words/phrases in a message.
        Arguments:
            message (str): The message from the user.
        Returns:
            Dict[str, int]: A count of each tag found in the message.
        """
        counter = Counter()
        msg = message.lower()
        for phrase, tags in self.TAGS.items():
            if re.search(r'\b' + phrase.lower() + r'\b', msg):
                counter.update(tags)
        return counter

class oxycsbot(ChatBot):

    STATES = [
        'waiting',
        'thoughts_1',
        'thoughts_2',
        'increase_reason_1',
        'increase_reason_2',
        'unknown_benefit_1',
        'unknown_benefit_2'
    ]

    TAGS = {
        # hello
        'Hello': 'hello',
        'hey': 'hello',
        'hi': 'hello',
        "what'sup": 'hello',
        'whats up': 'hello',
        'whats up?': 'hello',
        'hello':'hello',

        # generic
        'thanks': 'thanks',
        'okay': 'success',
        'bye': 'success',
        'yes':'yes',
        'yep':'yes',
        'no':'no',
        'nope':'no',

        #positive tags
        'ok':'yes',
        'okay':'yes',
        'sounds good':'yes',
        'yes':'yes',
        'all right':'yes',
        'very well':'yes',
        'of course':'yes',
        'by all means':'yes',
        'sure':'yes',
        'certainly':'yes',
        'absolutely':'yes',
        'indeed':'yes',
        'right':'yes',
        'affirmative':'yes',
        'agreed':'yes',

        #negative tags
        'no':'no',
        'nope':'no',
        'absolutely not':'no',
        'most certainly not':'no',
        'of course not':'no',
        'under no circumstances':'no',
        'by no means':'no',
        'not at all':'no',
        'negative':'no',
        'never':'no',
        'not really':'no',

    }


    #BENEFITS = ['increase_salary',
    #            'more_paid_time_off',
    #]


    def __init__(self):
        """Initialize the OxyCSBot.
        The `benefits` member variable stores whether the target
        benefit has been identified.
        """
        super().__init__(default_state='waiting')
        self.benefits = None


        # "waiting" state functions

    def respond_from_waiting(self, message, tags):
        #self.increase_salary = None
        #self.more_paid_time_off = None
        #print(tags)
        if 'hello' in tags:
            return self.go_to_state('thoughts_1')
        else:
            return self.finish('hello')


        #thoughts_1 state functions
    def on_enter_thoughts_1(self):
        response = "Hello boss, I would like to discuss increasing my salary. Can I discuss this with you?"
        return response

    def respond_from_thoughts_1(self, message, tags):
        if 'yes' in tags:
            return self.go_to_state('increase_reason_1')
        if 'no' in tags:
            return self.go_to_state('thoughts_2')
        else:
            return self.go_to_state('unknown_benefit_1')


            # "increase_reason_1" state functions
    def on_enter_increase_reason_1(self):
        reason_1 = "I believe that I deserve an increase in salary because for the past year I have consistently submit top quality work benefitting the company image and stock value. So what do you think?"
        return reason_1

    def respond_from_increase_reason_1(self, message, tags):
        if 'yes' in tags:
            return self.finish('success')
        if 'no' in tags:
            return self.go_to_state('thoughts_2')
        else:
            return self.go_to_state('unknown_benefit_1')


            #thoughts_2 state functions
    def on_enter_thoughts_2(self):
        response_2 = "Ok, then can I please discuss more paid time off?"
        return response_2

    def respond_from_thoughts_2(self, message, tags):
        if 'yes' in tags:
            return self.go_to_state('increase_reason_2')
        if 'no' in tags:
            return self.finish('reject')
        else:
            return self.go_to_state('unknown_benefit_2')


            # "increase_reason_2" state functions
    def on_enter_increase_reason_2(self):
        reason_2 = "I believe I have worked without taking any paid time off for the past 6 months and produced top quality work consistently so I think a little break would be nice. What do you think about this?"
        return reason_2

    def respond_from_increase_reason_2(self, message, tags):
        if 'yes' in tags:
            return self.finish('success')
        if 'no' in tags:
            return self.finish('reject')
        else:
            return self.go_to_state('unknown_benefit_2')


            # "unknown_benefit_1" state functions
    def on_enter_unknown_benefit_1(self):
        return self.finish('confused')

    def respond_from_unknown_benefit_1(self, message, tags):
        if 'yes' in tags:
            return self.go_to_state('increase_reason_1')
        else:
            return self.finish('fail')


            # "unknown_benefit_2" state functions
    def on_enter_unknown_benefit_2(self):
        return self.finish('confused')

    def respond_from_unknown_benefit_2(self, message, tags):
        #for increase_salary in self.BENEFITS:
            if 'yes' in tags:
                #self.increase_salary = increase_salary
                return self.go_to_state('increase_reason_2')
            else:
                return self.finish('fail')



        # "finish" functions

    def finish_confused(self):
        return "I am sorry I do not understand what you are saying. Could we please get back to the topic at hand?"

    def finish_hello(self):
        return "I am sorry I do not understand. Can you please say hello"

    def finish_success(self):
        return 'Great, thank you so much!'

    def finish_fail(self):
        return "I am sorry, I still do not understand what you are trying to say. Maybe we can discuss this again at a later point."

    def finish_reject(self):
        return "Ok, I understand. Thank you for your time."

    #def finish_thanks(self):
        #return "You're welcome!"


if __name__ == '__main__':
    oxycsbot().chat()
