def isolate_kunning(ctx):
    author = ctx.author 
    info = [
        f"**id:** {author.id}",
        f"**name (username handle):** {author.name}",
        f"**discriminator:** {author.discriminator}",   
        f"**str(author):** {str(author)}",              
        f"**global_name (Display Name):** {author.global_name}",
        f"**display_name (guild-aware):** {author.display_name}",
        f"**nick (nickname, guild only):** {getattr(author, 'nick', None)}",
        f"**mention:** {author.mention}",
    ]

    print(info)

    return False
