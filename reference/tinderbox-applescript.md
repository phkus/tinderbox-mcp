# AppleScript - Tinderbox Help

Tinderbox now offers limited AppleScript support, making it easier to automate workflows with other applications.

Some sample expressions that Tinderbox supports include:

---

```
set myNote to make new note in document "Workspace.tbx"
set myAgent to make new agent in myNote
```

…creates a new top-level note, and creates an agent in that note.

---

```
set name of myNote to "inbox"
```

…sets the name of the note created in the preceding line.

---

```
set value of (attribute of myNote named "Width") to 5
get notes in myNote
```

…returns a list of all the notes inside myNote.

---

```
get agents in myNote
get adornments in myNote
```

…returns a list of the agents and adornments inside myNote.

---

```
set value of (attribute of myNote named "Width") to 5
```

…sets the value of an attribute, here $Width

---

```
get value of (attribute of lastChild of MyNote named "Width")
```

…fetches the value of the designated attribute. Note the parentheses in this and the preceding example. They’re ugly, but AppleScript seems to compel this.

---

```
delete value of (attribute of myNote named "Width")
```

…removes any local value assigned to that attribute, restoring the inherited or default value.

---

You can get or set the default value of an attribute:

```
get defaultValue of (attribute of myNote named "Width")
set defaultValue of (attribute of myNote named "Width") to "5"
```

Or:

```
name of note 3 of document "Workspace.tbx"
```

Returns the name of the third top-level note in the specified document.

---

```
links of note 3 of document "Workspace.tbx"
```

returns a list of outbound links (excepting Web links) from the designated note.

---

```
find note in [note or document] with path "/path/to/note"
```

Returns a reference to the designated note. If the target is a document, the path should be an absolute path. If the target is a note, the path can be an absolute path or a relative path with respect to that note. For example: find note in myNote with path "parent" would return a reference to myNote’s container.

---

```
move myNote to theContainer
```

Moves a note to the specified container.

---

```
delete myNote
```

Deletes a note.

---

```
selected note of document "Workspace.tbx"
```

Returns the selected note. If several notes are selected, returns one of those notes, typically the first selected note. If no notes are selected, returns missing value.

---

```
selection of document "Workspace.tbx"
```

Returns a list of a selected notes

---

```
set selection of document "Workspace.tbx" to myNote
```

Selects a note. (At present, selecting more than one note is not supported.)

---

The expression

```
act on theNote with “action”
```

performs an action on the designated note. An action is typically one or more assignment or conditional statements, such as ``Color="red"`. Act on does not return a value. The expression

---

```
evaluate theNote with “expression”
```

returns the result of evaluating an expression. In an action, = means “assign”; in an expression, = means “comparison” (although the unambiguous operator == is preferred.)

---

The expression

```
refresh theNote
```

informs Tinderbox that a note has changed, and requests updates in the user interface.

---

Link types may also be created and modified.

```
make new linkType with properties {name: "example" }
set a to linkType named "agree"
set the dotted of a to true
```

Note that scripts can do very bad things to a document; keep great backups.


# Full AppleScript Documentation

## note

A Tinderbox note

### Elements
- notes
- links
- agents
- adornments
- attributes
- local attributes
- user attributes

Contained by: documents, notes

### Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| name | text | r/w | Its name |
| text | text | r/w | The note's text, without style |
| color | text | r/w | The note's color |
| child | note | r/o | First child |
| nextSibling | note | r/o | Next sibling |
| previousSibling | note | r/o | Previous sibling |
| parent | note | r/o | Container of this note |
| lastChild | note | r/o | Last child of this note |

### Commands

- find note in
- attribute of
- evaluate
- act on
- refresh
- move
- delete
- exists

---

## agent

A Tinderbox agent

Inherits from: note

---

## adornment

A Tinderbox adornment

Inherits from: note

---

## selection

Tinderbox selected notes

Inherits from: note

---

## link

A link between two notes

### Elements
Contained by: notes

### Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| source | note | r/o | Its source |
| destination | note | r/o | Its destination |
| path | text | r/o | Its path name |

---

## linkType

A link type

### Elements
Contained by: documents

### Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| name | text | r/o | Its name |
| color | text | r/w | Its color |
| visible | boolean | r/w | Its visibility |
| bold | boolean | r/w | Its boldness |
| dotted | boolean | r/w | Whether it is dotted |
| dashed | boolean | r/w | Whether it is dashed |
| linear | boolean | r/w | Whether it is linear |
| arrow | number | r/w | Its arrow type |
| action | text | r/w | Its action |
| broad | boolean | r/w | Whether it is broad |
| labeled | boolean | r/w | Whether its label is displayed |

---

## attribute

A Tinderbox attribute

### Elements
Contained by: documents, notes

### Properties

| Property | Type | Access | Description |
|----------|------|--------|-------------|
| name | text | r/w | Its name |
| type | text | r/w | Its type |
| defaultValue | text | r/w | Its default value |
| category | text | r/o | The attribute category |
| value | text | r/w | Its value |

---

## user attribute

An attribute you created

Inherits from: attribute

---

## local attribute

An attribute that has a local value, rather than an inherited or default value

Inherits from: attribute

---

## attribute properties

### Properties

| Property | Type | Description |
|----------|------|-------------|
| name | text | The name |
| type | text | The attribute type |

---

## link type properties

### Properties

| Property | Type | Description |
|----------|------|-------------|
| name | text | The name |

---

## find note in

Finds a note by its path

### Syntax

```
find note in specifier : The document or note
    with path text : The path
→ note : The note
```

---

## attribute of

Finds an attribute by name

### Syntax

```
attribute of specifier : any note
    named text : The attribute
→ attribute : The attribute
```

---

## evaluate

Evaluate a Tinderbox expression

### Syntax

```
evaluate text : The note for which the expression will be evaluated
    with text : The expression
→ text : The result
```

---

## act on

Perform a Tinderbox action

### Syntax

```
act on text : The note for which the action will be evaluated
    with text : The action
→ text : The result
```

---

## refresh

Ask the document to refresh its views

### Syntax

```
refresh text : ...
→ text : The result
```
