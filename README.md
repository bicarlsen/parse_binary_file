# Parse Binary File

> Install with `python -m pip install parse_binary_file`

Parse binary files by describing their structure.

## Components

### FieldDescription
Describes a field.

#### Properties
+ **type:** The type of the field being described.
    When loading data into the field it will be parsed based on the type.
    Valid types are:
    + **'bytes':** Leaves the value as bytes.
    + **'str':** String
    + **'int':** Integer, must be 4 bytes
    + **'float':** Float, must be 4 bytes
    + Any type may be wrapped in brackets `[]` to indicate the field is an array
      of that value type. Details of the elements are set using the `elements`
        property.
    [Default: 'bytes']

+ **name:** Name of the field.
    This is used to label the field.

+ **value:** The expected value of the field.
    This can be usedto indicate a specific value is expected for the field.

+ **size:** Number of bytes in the field.
    The last field can have a size of -1 which indicates the field continues to
    the end of the file.

+ **terminator:** Sequence of values indicating the end of the field.

+ **null_terminated:** Indicates the field is null terminated.
    Setting to `True` is equivalent to setting `terminator` to `0x00`.

+ **is_null:** Indicates the field only contains null bytes.
    Settings to true is equivalent to setting `value` equal to all null bytes.
    Must set `size` if `True`.

+ **description:** Description of the field.

+ **elements:** Used to specifiy the structure of the elements of an array.
    [TODO]

#### Methods
+ **FieldDescription(\**properties):** Initializes a new `FieldDescription` with
  the provided properties.


### Field
Contains information about a field, including its description and loaded value.

#### Properties
+ **desc:** `Field`'s description.

+ **value:** `Field`'s value.

+ **expected_value:** `self.desc.value`. Provided for convenience.

+ **size:** If the `Field`'s value is set, returns its size.
    If the `Field`'s value has not yet been set return the `Field`'s expected size if available.

+ **data:** Original data as bytes.

+ **value_matches:** If the `Field`'s loaded value matches that expected by the
  description. If no value was specified by the description returns `True`

+ Values of the `Field`'s description are available directly as well. 

#### Methods
+ **Field(desc: FieldDescription):** Initializes a new `Field`.
    `desc` should describe the field.

+ **from_dict(desc: dict):** Initializes a new `Field` using `desc` as its
  description.

+ **set_value(val: bytes, \**options):** Sets the value of the `Field` based on
    its description and the provided value.
    `**options` are additional arguments to specify how to parse the value.


### Data
Represents data from a file.

#### Properties
+ **info:** 

+ **fields:**

+ **defaults:**

+ **is_loaded:** If data has been loaded yet.

+ **value:** Value of the loaded data, or `None` if it has not yet been loaded.
    If loaded, the value is a list of teh value for each field.

+ **named_field_values:** Returns a dictionary of name-vlaue pairs for named `Field`s.

#### Methods
+ **from_dicts(desc: list[dict]):** Instantiates a new `Data` from a list of
  dictionaries describing its fields.

+ **keys():** Returns a list of named `Field`s names.

+ **load(stream: io.RawIOBase):** Loads data from a readable stream.


## Use
This library is intended to be used by describing the struture of a binary file
format in a configuration file. That file is then loaded and used to create a
`Data` instance. The `Data` instance can then `load()` data from a file and
assort it into the correct fields.

### Example
We would like to describe a new binary file format of `.msg`.
| Offset | Size | Name     | Description                                          |
| ------ | ---- | -------- | ---------------------------------------------------- |
| 0x00   | 0x02 | head     | `0xff 0x00` Indicates the file is a `.msg` file.     |
| 0x02   | 0x04 | size     | Total size of the file.                              |
| 0x06   | 0x04 |  --      | Null bytes to separate header from body.             |
| 0x0a   |  --  | greeting | Message greeting.                                    |
|  --    |  --  | message  | Message content.                                     |


We can describe this structure in a YAML file.
`msg.yaml`
```yaml
- name: 'head'
  value: "\xff\x00"

- type: 'int'
  name: 'file_size'
  description: 'Size of file in bytes'

- size: 4
  is_null: true

- type: 'str'
  null_terminated: True
  name: 'greeting'

- type: 'str'
  size: -1
  name: 'message'
```

To read a `.msg` file we can use the description of it.
```python
import os
import yaml  # use pyyaml to load `msg.yaml`
import parse_binary_file as pbf


# load description
with open('msg.yaml') as f:
    msg_desc = yaml.safe_load(f)
    
# create fields
fields = [pbf.Field.from_dict(f) for f in msg_desc]

# create data
data = pbf.Data.from_dicts(msg_desc, info = {'byte_order': 'little'})

with open('my_message.msg', 'rb') as f:
    data.load(f)

is_corrupt = (data['file_size'] != os.path.getsize('my_message.msg'))
greeting = data['greeting'].value
message = data[-1].value
```
