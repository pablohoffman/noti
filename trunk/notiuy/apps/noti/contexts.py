def noti(request):
    return {
        'cssfile': request.session['cssfile'],
        'msie': request.session['msie'],
        'msienew': request.session['msienew'],
    }
