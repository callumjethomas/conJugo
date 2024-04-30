# *con*Jugo
## Video Demo:  https://www.youtube.com/watch?v=16fqDeRrZAk
## Description:
*con*Jugo is a web app which helps you learn and practice the conjugation of French verbs.

## Features:

- See the full conjugation table for any verb you choose in *Conjugate* mode.
- Practice and improve your memorisation of these conjugations in the flashcard-like *Practice* mode.
- Choose from a pre-prepared list of the top 100 most common regular and irregular French verbs, or add up to 20 of your own custom verbs to practice.
- Choose the tenses and moods you want to practice to adjust the *Practice* mode experience to suit your current language learning level.
- Review your correct and incorrect answers at the end of each *Practice* round, allowing you to highlight which conjugations you need to focus on.
- Save your custom verb lists to your account to revisit whenever you want.
- *con*Jugo uses the [mlconjug3 Python library](https://github.com/Ars-Linguistica/mlconjug3), which utilises machine learning to predict the correct conjugation of any possible French verb with high accuracy, even totally novel, slang or made-up verbs!

## Dependencies:

- Python 3.11.7
- Flask 3.0.3
- [`mlconjug3` v.3.10.4](https://github.com/Ars-Linguistica/mlconjug3)
- [`flask-session` v.0.6.0](https://flask-session.readthedocs.io/en/latest/)
- [`cs50` library for Python](https://cs50.readthedocs.io/libraries/cs50/python/)

> [!IMPORTANT]
> `mlconjug3` is currently not compatible with Python 3.12.2

## Structure

### `site.db`
SQLite database which holds the user and verb information for the app.
This database schema can created using the commands in the file `static/create_db.sql`

The database is structured as follows:

[![](https://mermaid.ink/img/pako:eNp9kk1vgzAMhv8K8plWLd9wHpp22A5bD9OEVGXELagjQUnYxij_fSFtWb9WkBB-4ve1De4g5xQhARR3JVkLUmUsY1YjUUir02_6enhapPfps4HLku7gIn1dGMJIhUeoILIYwn7wkTkXmBNBz63Gg9HvdpElYfILxRHVBtpBnRwcPGpeMiXHLj5RvF8MM8DTOmeDqLZG69_ejHHFOb0wHuB1Y6NRyCReiAy9obL2f2S7nUx49_f5rMTKYKWDcs2sDbYZXMnezX81c7jBhgpFRUqq18D0lYEqUFeHQUOJ2AzJvc4jjeIvLcshUaJBG5qaEoX7xYFkRT7kSFNaKi5GWBP2xnl1UOoQkg6-IXGcaBr7ketEjhfOwplrQ6tp4E9dTz_nbhDOo9Dvbfgx-tk0iON47kWB68ex43k2oCn1uFtks8_9Lz3E6Fw?type=png)](https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNp9kk1vgzAMhv8K8plWLd9wHpp22A5bD9OEVGXELagjQUnYxij_fSFtWb9WkBB-4ve1De4g5xQhARR3JVkLUmUsY1YjUUir02_6enhapPfps4HLku7gIn1dGMJIhUeoILIYwn7wkTkXmBNBz63Gg9HvdpElYfILxRHVBtpBnRwcPGpeMiXHLj5RvF8MM8DTOmeDqLZG69_ejHHFOb0wHuB1Y6NRyCReiAy9obL2f2S7nUx49_f5rMTKYKWDcs2sDbYZXMnezX81c7jBhgpFRUqq18D0lYEqUFeHQUOJ2AzJvc4jjeIvLcshUaJBG5qaEoX7xYFkRT7kSFNaKi5GWBP2xnl1UOoQkg6-IXGcaBr7ketEjhfOwplrQ6tp4E9dTz_nbhDOo9Dvbfgx-tk0iON47kWB68ex43k2oCn1uFtks8_9Lz3E6Fw)

#### `users`
Stores the user data for the app.
- **user_id**: Primary key for the table.
- **username**: Unique username entered by the user upon registration.
- **hash**: Hashed password (created using `generate_password_hash` function from `werkzeug.security` library).

#### `verbs`
The database comes preloaded with verbs taken from a list of <a href="https://www.linguasorb.com/french/verbs/most-common-verbs/">100 most common French verbs</a> published by linguasorb.
- **verb_id**: Primary key for the table.
- **name**: Infinitive form of the verb.
- **type**: Either 'regular' or 'irregular' (based on linguasorb verb list), or 'custom' if entered by user.
- **user_id**: Foreign key referencing `users` table. NULL for preloaded verb.

> [!NOTE]
> Including the `user_id` field enables users to add their own custom verbs to the database.
#### `scorecard`
Stores the answers the user has entered for the current *Practice* round and allows the app to calculates a score for the user by comparing the user's answer to the correct answer for the corresponding question.

- **scorecard_id**: Primary key for the table.
- **user_id**: Foreign key referencing `users` table.
- **user_answer**: Answer input by the user for a question.
- **correct_answer**: The correct answer to the corresponding question.
- **points**: Stores a point for each correct answer as an integer (1 if correct, 0 if incorrect).

> [!WARNING]
> Scorecard data is *not* persistent between rounds or sessions, data is wiped at the end of each *Practice* round for each user.

#### `moods`
List of possible grammatical moods, for reference by `app.py`.
- **mood_id**: Primary key for the table.
- **name**: Name of grammatical mood.

#### `tenses`
List of possible grammatical tenses, for reference by `app.py`.
- **tense_id**: Primary key for the table.
- **name**: Name of grammatical tense.

---

### `helpers.py`
Python file which contains helper functions used in the main `app.py` file.

#### `login_required(f)`
Decorator which can be added to `app.py` routes. Redirects the user to the login page if `session` determines they are not logged in due to there being no `user_id` variable stored for the current `session`.

#### `validate(password)`
Function to validate the password entered upon registration. Requires that the password:
  - is at least 8 characters long,
  - contains at least one uppercase and one lowercase alphabetical character,
  - contains at least one numerical digit.

#### `generate_result()`
This is the main function which does the work of generating a random conjugation from a user-selected set of verbs, moods and tenses. It returns:
1. a verb,
2. a pronoun,
3. a mood,
4. a tense,
5. the conjugated form of the verb for the above mood and tense, with the pronoun.

In brief this function:
1. Picks a verb at random from the verb list(s) the user has indicated to use, using the `choice` function from the `random` library.
2. Picks a tense/mood at random to use from the options the user has indicated, in the same way.
3. Uses the `Conjugator()` class from the `mlconjug3` library to create a `VerbFr` object, which is essentially a list of dictionaries.
4. Picks a pronoun at random from the keys stored in the `VerbFr` object dictionary for the chosen mood and tense.
5. Finds the final conjugated form of the verb by indexing the `VerbFr` object using the chosen mood, tense and pronoun.

Special conditions:
- There is a bug in `mlconjug3` caused by the unusual nature of the French verb *falloir*. To work around this, the results for this verb have had to be hard-coded.
- Some moods and tenses do not have pronouns associated with them. These have had to be worked around to avoid generating key errors.
- `mlconjug3` stores some pronouns together as a string (e.g. `'il, (elle on)'`). These have had to be separated manually to give the user each of these pronouns as an individual option.
- The pronoun *je* becomes *j'* when it occurs before a vowel. This has been accounted for at the end of this function.

---

### `app.py`
Main Python file which describes the routes for rendering the app pages in Flask.

#### `index`
Renders the `index.html` template (home page) for the app. This will redirect to the login page if the user is not logged in, otherwise it will allow them to go to the *Practice* or *Conjugate* pages.

#### `login`
Renders the `login.html` page template for the app, which allows the user to login.

In brief the `login()` function:
1. Clears all stored variables from the current `session`.
2. Checks the user has input a username and password.
3. Queries the `user` table in the database for the username.
4. Hashes the input password and compares it to the hash in the `user` table.
5. If correct, stores the current `user_id` as a variable in `session`.

#### `logout`
Logs the current user out, by clearing all the stored variables from the current `session`.

#### `register`
Renders the `register.html` page template for the app, which allows a user to register an account.

In brief the `register()` function:
1. Checks the user has input a username.
2. Checks that the input username does not already exist.
3. Checks the user has input a password.
4. Validates the password meets requirements using the `validate(password)` function from `helpers.py`
5. Checks the user has confirmed the password.
6. Checks this confirmation matches the initial password input.
7. Hashes the password.
8. Inserts the username and hash as a new entry in the `users` table in the database.

#### `account`
Renders the `account.html` page template for the app. Allows the user to either change their password (via the `change_pwd()` function), or delete their account entirely via the `delete` page.

In brief the `change_pwd()` function:
1. Ensures the current password for the user was submitted.
2. Hashes and checks this against the user's entry in the `users` table in the database.
3. Checks the user has input a new password and confirmation.
4. Checks the new password and confirmation match.
5. Validates the new password using the `validate(password)` function from `helpers.py`.
6. Hashes the new password.
7. Updates the user's entry in the `users` table to include the new password hash.

#### `delete`
Renders the `delete.html` page template for the app. Allows the user to delete their account entirely.

In brief the `delete` function:
1. Ensures the current password for the user was submitted.
2. Hashes and checks this against the user's entry in the `users` table in the database.
3. Deletes the user's entries in the `scorecard` and `verbs` tables in the database.
4. Deletes the user's entry in the `users` database.
5. Logs the user out by clearing the current `session` variables.

#### `credits`
Renders the `credits.html` page template. Shows credits for the app.

#### `verb_list`
Renders the `verb_list.html` page template. Shows verbs currently loaded in the database. This includes all the preloaded regular and irregular verbs, as well as any custom verbs the user has added.

In brief the `verb_list` function:
1. Obtains all the name and type of all the verbs currently stored in the `verbs` table in the database.
2. Returns the resulting verb list to the verb list page via POST, allowing it to be rendered as a table via jinja templating.
3. Also returns a `delete_all` variable to the verb list page if any custom verbs are in the database for the current user, to allow rendering of a 'Delete all' button via jinja templating.

#### `add_verb`
Allows the user to add up to 20 custom verb to the database.

In brief the `add_verb` function:
1. Gets the input verb from the form on the verb list page.
2. Checks that there are currently fewer than 20 verbs in the `verbs` table with the current user's `user_id`.
3. Checks the input verb is not currently one of the current user's custom verbs.
4. Checks the input verb is a valid verb according to `mlconjug3`.
5. Adds the input verb to the `verbs` table, along with the current user's `user_id`.

#### `delete_verb`
Allows the user to delete one or all of their custom verbs from the database.

In brief the `delete_verb` function:
1. Checks if the user has clicked the 'Delete all' button,
2. If so, deletes all custom verbs from the `verb` table with the current user's `user_id`.
3. If not, checks for which verb the user wants to delete and deletes that verb from the `verb` table.

> [!NOTE]
> The inputs for this function on the verb list page are buttons, not a text input. These buttons take the value from the verb they appear next to, so it is not possible for the user to delete custom verbs that do not exist.

#### `conjugate`
Renders the `conjugate.html` page template. This allows the user to use *Conjugate* mode to conjugate any verb they input and outputs a conjugation table.

In brief the `conjugate` function:
1. Takes the input from the `conjugate` page.
2. Attempts to conjugate the input verb using `mlconjug3.conjugate()`
3. Returns the resulting `VerbFr` conjugation object to the `conjugate` page via POST, allowing it to be rendered as a table via jinja templating.

> [!WARNING]
> There is a bug in `mlconjug3` caused by the unusual nature of the French verb *falloir*. To work around this, the results for this verb have had to be hard-coded in a separate html page.

#### `start`
Renders the `start.html` page template. This allows the user to select the verbs and moods/tenses they wish to practice, before beginning *Practice* mode.

In brief:

If the user arrives via 'GET' (*i.e.* from clicking the link on the home page), the `start` function:
1. Deletes all the existing stored `session` variables for verb types, moods, tenses and permutations.
2. Deletes all the scorecard database entries for the current user.
3. Sends the user to the start page via 'POST'.
This provides the user with a blank slate to start a new *Practice* round with.

If the user arrives via 'POST' (as they have just started a new *Practice* round), the `start` function:
1. Gets the verb types to include from the `verbtypes` input form on the start page and stores this as a `session` variable.
   - Includes error handling to ensure user selects at least one verb type and one tense.
   - Includes error handling in the case that the user selects 'custom' but doesn't have any custom verbs saved.
2. Get the verb moods and tenses to include from the `verbtenses` input form on the start page, and stores these as `session` variables.
3. Calculate the total possible number of permutations for the selected number of verbs, moods and tenses, and stores this as a `session` variable. This allows us to know when the *Practice* round should end.
4. Redirect the user to the `practice` page.

#### `practice`
Renders the `practice.html` page template. This allows the user to use *Practice* mode where they will have to guess the conjugation of a random verb displayed on the screen.

In brief the `practice` function:
1. Calculates the current 'score' by getting the sum of all the `points` variables stored in the `scorecard` table for the current user's `user_id`.
2. Calculates the current 'total' of points available so far by getting the total number of entries in the `scorecard` table for the current user's `user_id`. End the round if this total is equal to the maximum number of permutations for this round.
3. Uses the `generate_result` function from `helpers.py` to generate a random conjugation from the user's selected options.
4. Check if the generated result has already been generated and stored previously in the `scorecard` table under the current user's `user_id`. If it has, generate a new result. This ensures that each possible correct answer is only generated and stored once.
5. Store the correct answer from the function in the `scorecard` table as a new entry with the current user's `user_id`.
6. Render the `practice.html` template to show the user the question (verb, pronoun, mood and tense to use for the conjugation) and allow the user to input their answer.

#### `check`
Checks the answer the user has input once they click the 'Submit' button on the `practice` page. Renders either the correct page template or the incorrect page template.

In brief the `check` function:
1. Gets the latest entry in the `scorecard` table for the current user's `user_id`.
2. Gets the user's answer which was submitted from the input form on the `practice` page when they clicked 'Submit'.
3. If the user's answer is the same as the correct answer, update the entry in the scorecard table to include their answer and 1 point, then render the `correct.html` page template, with their current score and total via POST.
4. If the user's answer is **not** the same as the correct answer, update the entry in the `scorecard` table to include the user answer and 0 points, then render the `incorrect.html` page template, with current score and total via POST.

#### `scorecard`
Renders the `scorecard.html` page template which shows all the user's scorecard entries for this *Practice* round.

In brief the `scorecard` function:
1. Gets all the entries from the `scorecard` table for the current user's `user_id`.
2. Gets the sum of all points from these entries.
3. Gets the total number of entries.

#### `end`
Renders the `end.html` page template, which informs the user that the current *Practice* round is over and offers to redirect them to the scorecard page.
In brief the `scorecard` function:
1. Gets the sum of all points from these entries.
2. Gets the total number of entries.

#### Error handling
The `errorhandler` functionality is used to render custom error messages for commonly seen HTML error codes including 400, 404, 405 and 500.

---

### `layout.html`
Root template for html rendering.

<a href="https://getbootstrap.com/docs/5.3/getting-started/introduction/">Bootstrap 5.3.2</a> was used for CSS, Javascript and icon styling. A navbar was used at the top of each page to provide consistent look and branding across the whole app. This allows access to the home page, verb list, accounts and logout functions from any page in the app.

---

### `styles.css`
CSS file for overwriting some Bootstrap CSS values with custom CSS.

Most of the CSS styling is handled via <a href="https://getbootstrap.com/docs/5.3/getting-started/introduction/">Bootstrap 5.3.2</a>. However some custom CSS was used to overwrite Bootstrap values for navbar background, text and link colouring.
