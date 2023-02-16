async def get_prices(links: list, prices: list) -> dict:
	subs = []
	links = links
	prices = prices
	for l in links:
		for p in prices:
			try:
				if l.metadata.name == p.nickname:
					price = f"{(p.unit_amount / 100):.2f} €"
					price = price.replace(".", ",")
					subs.append(
						{
							"name": l.metadata.description,
							"price": p.unit_amount,
							"price_format": price,
							"url": l.url,
							"nickname": p.nickname,

						}
					)
			except Exception as e:
				print(e)

	subs = sorted(subs, key=lambda k: k['price'])
	return subs
