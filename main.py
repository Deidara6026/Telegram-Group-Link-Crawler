import classes
import config
import asyncio

web = []

async def init():
    print("""
    Welcome to the bot!
    To add new phone numbers, add them to the list in config.py
    to add new links, add them to the source.txt file(separated by commas)

    Enjoy!
    """)
    for i in config.phone_list:
        # See the class definitions in classes.py
        # We create a spyder for each phone number, and initialize it
        spyder = classes.Spyder(i, config.api_id, config.api_hash)  
        c = await spyder.initialize()
        web.append(spyder)
    # Populate the class lists
    classes.Spyder.crawl_list = config.chat_list
    await asyncio.gather(*[spyder.feed() for spyder in web])


if __name__=="__main__":
    asyncio.run(init())