import response_system_extensions as rse
from apps.seasons.models import Season
from response_system import Response


async def send_award_points_message(client, subscription, bonus) -> Response:
    """ ... """

    season = Season.get_current()
    is_prize_bought = season.current_prize.is_bought_by_client(client.chat_id)
    return rse.tmpl_send('apps/seasons/templates/message-season-points-given.xml', {
        'is_prize_bought': is_prize_bought,
        'client': client,
        'season': season,
        'subscription': subscription,
        'bonus': bonus,
    })