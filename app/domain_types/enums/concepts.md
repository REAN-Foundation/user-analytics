#### Difference between Event Type, Event Category and Event Subject

##### Event Types
Event types can broadly be termed as actions - user, system, device, etc. These are generally verbs or verb phrases. For example - `medication-create`, `user-login`, `device-connect`, etc.

##### Event Categories
Event categories are broad categories of events. These are generally nouns. For example - 'Medication' 'Assessment', etc. **The application features are considered as event categories.**. These are used to group similar events together. For example, all events related to medication can be grouped under 'Medication' category.

##### Event Subjects
Event subjects are somewhere between event categories and event types as far as granularity is considered.
They are basically the 'subject' of the event (event-action).
For example,
- If the event type is 'MedicationScheduleTaken (`medication-schedule-taken`)' and
- and the event category is 'Medication (`medication`)',
- then the subject here is 'MedicationSchedule (`medication-schedule`)'

It is also possible that names of the event-category and event subject is same. For example,
- If the event type is 'MedicationCreate (`medication-create`)' and
- and the event category is 'Medication (`medication`)',
- then the subject here is 'Medication (`medication`)'

Please note that - Event subjects are not always enumerated as enums. They can be dynamic as well.
For example, screen-names (For example- screen named `dashboard`) for event category `app-screen-visit` and event type `screen-entry`. In such cases, the event subject can be a any string.
