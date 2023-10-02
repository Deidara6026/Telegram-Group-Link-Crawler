## Telegram Spyder

This is a command-line tool designed to crawl telegram links, and store them in a csv file. Supports multiple accounts. Just add the phone numbers to the phone list in config.py!

# Usage

```bash
python3 main.py
```

```python
import main.init as main
import asyncio

asyncio.run(main())
 ```
Or to use the class directly in your own code,

```python
import classes
import asyncio

async def main():
    # name parameter is the telegram phone number
    spyder = classes.Spyder(name, api_id, api_hash)  
    await spyder.initialize()
    # populate the spider's web
    classes.Spyder.crawl_list = ["t.me/botdevelopment"]
    await spyder.feed()
asyncio.run(main())
```

Spyder.feed() is an async function which takes in one telegram account, so you can run multiple spiders
(multiple accounnts) using asyncio.gather()

```python
web=[]
chat_list=["t.me/botdevelopment"]
for i in phone_list:
    # See the class definitions in classes.py
    # We create a spyder for each phone number, and initialize it
    spyder = classes.Spyder(i, api_id, api_hash)  
    # Login to the account
    c = await spyder.initialize()
    # Add to a list
    web.append(spyder)
# Populate the class lists
classes.Spyder.crawl_list = chat_list
await asyncio.gather(*[spyder.feed() for spyder in web])

```

## License

[MIT](https://choosealicense.com/licenses/mit/)