import telethon
from telethon.errors.rpcbaseerrors import BadRequestError
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.types import InputMessagesFilterUrl
from telethon.types import PeerChat
from telethon.utils import get_display_name
import config
import asyncio
import re
import pandas
import os


class Spyder:
    # All spyders have the same lists, to prevent redundancy and save memory 
    crawl_list = []
    output_list = []
    tracking_list = []
    errors = []

    def __init__(self, name, api_key, api_hash):
        self.api_key = api_key
        self.api_hash = api_hash
        self.name = name
        self.client = None
    
    async def initialize(self) -> telethon.TelegramClient:
        """
        Start the client and assign it to the class instance
        """
        client = telethon.TelegramClient(self.name, api_id=self.api_key, api_hash=self.api_hash, proxy=config.proxy)
        print("Beginning log in sequence for ", self.name)
        await client.start(phone=self.name)
        print("\n")
        await asyncio.sleep(1)
        self.client = client
        return client
    
    async def _crawl(self):
        """
        Crawl all links starting from the seed in the config file.
        Do not call this method alone, as it does not store the links.
        call feed instead 
        """
        # get a group from the list
        if self.client == None:
            raise(AttributeError("CLient not found"))
        while len(self.crawl_list) > 0:
            try:
                group_link = self.crawl_list.pop()
                await self.client.get_dialogs()
                chat = await self.client.get_input_entity(group_link)
                try:
                    async for message in self.client.iter_messages(chat, filter=InputMessagesFilterUrl, search='t.me'):
                        text = message.raw_text
                        # Regex for finding links in the text, and then a bit of filtering
                        urls = re.findall('http[s]?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)+re.findall('t?.me/(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
                        urls = [x.lower() for x in urls if "t.me/" in x or "telegram.me/" in x or "telegram.dog/" in x]

                        for i in urls:
                            try:
                                # Filter out some bad urls
                                if i in ["https://telegram.dog", "t.me/botfather", "https://telegram.me", "t.me/username", "t.me/durov"]:
                                    continue
                                if i in self.tracking_list:
                                    continue
                                if i in self.errors:
                                    continue
                                if i[-3:] == "bot" or i[-3:] == "Bot" or i[-3:] == "BOT":
                                    continue
                                # attempt to get the entity using the link. will produce an exception if the link is not valid
                                # that exception is caught, and the link is added to errors and skipped
                                chat = await get_display_name(i)
                                if chat == "":
                                    continue
                                if any(s in chat for s in config.keyword_whitelist):
                                    if any(d in chat for d in config.keyword_blacklist):
                                        continue
                                    print(i)
                                    self.output_list.append(i)
                                    self.tracking_list.append(i)
                                    self.crawl_list.append(i)
                                    await asyncio.sleep(10)
                            except Exception as e:
                                self.errors.append(i)
                                continue
                except Exception as e:
                    print(e)
                    continue
            except FloodWaitError as e:
                await asyncio.sleep(50000)
                print("Error:", group_link, e)
                continue

            
    async def feed(self):
        """
        Calls _crawl and records its data in chat_list.csv every 5 minutes 
        """
        while True:
            await self._crawl()
            await asyncio.sleep(5*60)
            # Export the gathered data every 5 minutes
            if os.path.exists("chat_list.csv"):
                old = pandas.read_csv("chat_list.csv")
                links = old["links"].tolist()
                # add the old data to the new and export to csv
                pandas.DataFrame(self.output_list+links, columns=["links"]).to_csv("chat_list.csv", columns=["links"])
                self.output_list = []
                continue
            pandas.DataFrame(self.output_list, columns=["links"]).to_csv("chat_list.csv", columns=["links"])
            self.output_list = []
            continue



                