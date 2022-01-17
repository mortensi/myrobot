# myrobot
Static analysis of MySQL diagnostics

## Usage

Collect MySQL diagnostics like:

```
TEE diag.txt;
CALL sys.diagnostics(60, 60, 'current');
NOTEE;
```

And invoke like:

```
python myrobot.py diag.txt
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
