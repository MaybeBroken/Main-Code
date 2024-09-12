def cli():
    from characterai import aiocai
    import asyncio


    async def main():
        char = input("CHAR ID: ")

        client = aiocai.Client("6af6433e59044578025d9786262aafab39f95d78")

        me = await client.get_me()

        async with await client.connect() as chat:
            new, answer = await chat.new_chat(char, me.id)

            print(f"{answer.name}: {answer.text}")

            while True:
                text = input("YOU: ")

                message = await chat.send_message(char, new.chat_id, text)

                print(f"{message.name}: {message.text}")


    asyncio.run(main())
def auth():
    from characterai import aiocai, sendCode, authUser
    import asyncio

    async def main():
        email = input('YOUR EMAIL: ')

        code = sendCode(email)

        link = input('CODE IN MAIL: ')

        token = authUser(link, email)

        print(f'YOUR TOKEN: {token}')

    asyncio.run(main())

cli()