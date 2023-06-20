# MyRobot

This script performs static analysis of MySQL diagnostics. Diagnostics are collected using the [`sys.diagnostics`](https://dev.mysql.com/doc/refman/8.0/en/sys-diagnostics.html) procedure.


## Usage

Collect MySQL diagnostics like:

```
TEE diag.txt;
CALL sys.diagnostics(60, 60, 'current');
NOTEE;
```

And invoke the script like:

```
python3 myrobot.py diag.txt
```


## Sample output

![demo](demo.gif)


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License

[MIT](https://choosealicense.com/licenses/mit/)
