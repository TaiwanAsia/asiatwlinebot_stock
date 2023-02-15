$(document).ready(function () {


    load_data();

    function load_data(keyword='null') {
        if(keyword != 'null' && keyword != ''){
            $.ajax({
                type: 'POST',
                url: "/search_stream",
                data: {
                    'data': keyword
                },
                dataType: 'json'
            })
            .done(function (data) {
                companies = data['data']
                if(companies.length > 0){
                    $('#companies').empty()
                    Object.keys(companies).forEach((key) => {
                        console.log(key, companies[key])
                        $('#companies').append(new Option(companies[key], companies[key]))
                    });
                }
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                console.log('GG')
            });
        }
    }
    
    var keyinTime;//此為需要事先定義要記錄的定時器
    $('#search').keyup(function() {
        var keyword = $(this).val();
        clearTimeout(keyinTime);//要清掉正在計時的事件，要不然會多重運行
        keyinTime = setTimeout(function(){ 
            load_data(keyword);
        }, 100)
        
    })
})