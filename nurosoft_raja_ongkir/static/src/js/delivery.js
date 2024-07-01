odoo.define('nurosoft_raja_ongkir.delivery', function (require) {
"use strict";
	var core = require('web.core');
    var publicWidget = require('web.public.widget');

    var _t = core._t;
    var concurrency = require('web.concurrency');
    var dp = new concurrency.DropPrevious();
    var ajax = require('web.ajax');

    var $pay_button = $('#o_payment_form_pay');
    var $delivery_container = $('#delivery_method');

    var $ekspedisi_container = $('#ekspedisi-container');
    var $select_city = $('#select-city');
    var $select_city_id = $('#raja_ongkir_city');
    var $select_ekspedisi = $('#select-ekspedisi');
    var $list_ekspedisi = $('#list-ekspedisi');
    var $list_city_container = $(".list-city-container");
    var $error_container = $("#error-container");

    var city = 0;
    var ekspedisi = '';
    var carrier_id = 0;
    var is_raja_ongkir = false;
    var raja_ongkir_destination_type = 'city';

    
    var setErrorMessage = function(show,text){
        if(show){
            $error_container.text(text);
            $error_container.show(); 
        }else{
            $error_container.text('');
            $error_container.hide(); 
        }
    }

    publicWidget.registry.websiteSaleDelivery.include({
        start: function () {
            var self = this;
            var $carriers = $('#delivery_carrier input[name="delivery_type"]');
            // Workaround to:
            // - update the amount/error on the label at first rendering
            // - prevent clicking on 'Pay Now' if the shipper rating fails
            if ($carriers.length > 0) {
                $carriers.filter(':checked').click();
            }

            // Asynchronously retrieve every carrier price
            _.each($carriers, function (carrierInput, k) {
                self._showLoading($(carrierInput));
                self._rpc({
                    route: '/shop/carrier_rate_shipment',
                    params: {
                        'carrier_id': carrierInput.value,
                    },
                }).then(self._handleCarrierUpdateResultBadge.bind(self));
            });            

            $select_ekspedisi.on('change', function(){
                ekspedisi = $(this).val();
                self.check_cost(city, ekspedisi);
            }); 

            if($select_ekspedisi){
                self.get_ekpedisi();
            }

            return this._super.apply(this, arguments);
        },

        _handleCarrierUpdateResult: function (result) {
            this._handleCarrierUpdateResultBadge(result);
            var $payButton = $('button[name="o_payment_submit_button"]');
            var $amountDelivery = $('#order_delivery .monetary_field');
            var $amountUntaxed = $('#order_total_untaxed .monetary_field');
            var $amountTax = $('#order_total_taxes .monetary_field');
            var $amountTotal = $('#order_total .monetary_field, #amount_total_summary.monetary_field');

            if (result.status === true) {
                $amountDelivery.html(result.new_amount_delivery);
                $amountUntaxed.html(result.new_amount_untaxed);
                $amountTax.html(result.new_amount_tax);
                $amountTotal.html(result.new_amount_total);
                $payButton.data('disabled_reasons').carrier_selection = false;
                $payButton.prop('disabled', _.contains($payButton.data('disabled_reasons'), true));
                
                if(!is_raja_ongkir || $('.ekspedisi-selected').length > 0){
                    $pay_button.prop('disabled', false);                
                }else{
                    $pay_button.prop('disabled', true);                
                }

            } else {
                $amountDelivery.html(result.new_amount_delivery);
                $amountUntaxed.html(result.new_amount_untaxed);
                $amountTax.html(result.new_amount_tax);
                $amountTotal.html(result.new_amount_total);
            }
        },
        _onCarrierClick: function (ev) {
            var $radio = $(ev.currentTarget).find('input[type="radio"]');
            this._showLoading($radio);
            $radio.prop("checked", true);
            var $payButton = $('button[name="o_payment_submit_button"]');
            $payButton.prop('disabled', true);
            $payButton.data('disabled_reasons', $payButton.data('disabled_reasons') || {});
            $payButton.data('disabled_reasons').carrier_selection = true;
            carrier_id = $radio.val();
            this.check_carrier();
        },
        check_carrier: function(){
            $.blockUI();
            var self = this;
            var values = {'carrier_id': carrier_id};
            ajax.jsonRpc('/shop/get_carrier_type', 'call', values)
            .then(function(result){
                $.unblockUI();
                $pay_button.prop('disabled', false);
                if(result.city){
                    $("#destination-city").text(result.city)
                }
                if(result.delivery_type == 'raja_ongkir'){
                    $ekspedisi_container.show();
                    is_raja_ongkir = true;
                    var $carriers = $('#delivery_method input[name="delivery_type"]');
                    if($carriers.length > 1){
                        self.check_cost();
                    }
                    self._rpc({route:'/shop/current_carrier', params: values})
                        .then(self._handleCarrierUpdateResult.bind(self));               
                }else{
                    is_raja_ongkir = false;
                    $ekspedisi_container.hide();
                    self._rpc({route:'/shop/update_carrier', params: values})
                        .then(self._handleCarrierUpdateResult.bind(self));
                }  
            },function(err){
                $.unblockUI();
                $pay_button.prop('disabled', false);
            });
        },

        get_ekpedisi: function(){
            var self = this;     
            ajax.jsonRpc('/shop/get_carrier_list', 'call', {}).
            then(function(result){
                $select_ekspedisi.html('');
                result.forEach(function(item){
                    var option = '<option value="' + item['code'] + '">' + item['name'] + '</option>';
                    $select_ekspedisi.append(option);
                });
                ekspedisi = $select_ekspedisi.val();
                self.check_cost();
            },function(err){
                // framework.unblockUI();
            });
        },        

        check_cost: function(){
            if(ekspedisi == '' || $delivery_container.html() == undefined){
                return;
            }
            $.blockUI();
            var self = this;
            $pay_button.prop('disabled', true);
            $list_ekspedisi.html('');
            var values = {
                'carrier_id': carrier_id,
                'ekspedisi': ekspedisi
            };
            ajax.jsonRpc('/shop/get_carrier_cost', 'call', values)
            .then(function(result){
                $.unblockUI();
                if(result.rajaongkir){
                    var costLength = 0;
                    if(result.rajaongkir.results){
                        result.rajaongkir.results.forEach(function(item){
                            costLength += item.costs.length;
                        });
                    }

                    if(result.rajaongkir.status.code != 200){
                        setErrorMessage(true, result.rajaongkir.status.description);
                    }else if(costLength == 0){
                       setErrorMessage(true, 'Layanan tidak tersedia. Coba beberapa saat lagi, pilih ekpedisi lain atau pilih kota terdekat.'); 
                    }else{
                        setErrorMessage(false, '');
                    }
                }else if(result.norajaongkir){
                    setErrorMessage(false, '');
                }else{
                    setErrorMessage(true, 'Terjadi kesalahan ! Coba lagi.');
                }
                if(result.rajaongkir && result.rajaongkir.status.code == 200){
                    var tujuan = result.rajaongkir.origin_details.city_name ? result.rajaongkir.origin_details.type + ' ' + result.rajaongkir.origin_details.city_name : result.rajaongkir.origin_details.subdistrict_name + ' ' + result.rajaongkir.origin_details.type + ' ' + result.rajaongkir.origin_details.city;
                    if(raja_ongkir_destination_type == 'city'){                    
                        tujuan += ' (' + result.rajaongkir.origin_details.province;
                        tujuan += ') -> ' + result.rajaongkir.destination_details.type + ' ' + result.rajaongkir.destination_details.city_name;
                        tujuan += ' (' + result.rajaongkir.destination_details.province + ')';
                    }else{
                        tujuan += ' (' + result.rajaongkir.origin_details.province;
                        tujuan += ') -> ' + result.rajaongkir.destination_details.subdistrict_name + ' ' + result.rajaongkir.destination_details.type + ' ' + result.rajaongkir.destination_details.city;
                        tujuan += ' (' + result.rajaongkir.destination_details.province + ')';
                    }
                    
                    var weight = result.rajaongkir.query.weight;

                    result.rajaongkir.results.forEach(function(itemHeader){
                        itemHeader.costs.forEach(function(item){
                            var delivery_object = {
                                'name': itemHeader.name,
                                'description': item.description,
                                'etd': item.cost[0].etd,
                                'value': item.cost[0].value,
                                'city': tujuan,
                                'weight': weight,
                            };
                            var delivery_info = window.btoa(JSON.stringify(delivery_object));
                            var element = '<div class="col-md-6 ekspedisi-detail">';
                            element += '<div class="card">';
                            element += '<div class="card-body">';
                            element += '<h4>' + itemHeader.name + '</h4>';
                            element += '<p><span class="badge">' + item.description + '</span></p>';
                            element += '<p>Perkiraan sampai ' + item.cost[0].etd + ' hari</p>';
                            element += '<p><b>Rp. ' + item.cost[0].value + '</b></p>';
                            element += '<input type="hidden" class="ekspedisi_value" value="' + delivery_info + '" />';
                            element += '</div></div></div>';

                            $list_ekspedisi.append(element);
                        });
                    });
                    $(".ekspedisi-detail").click(function(e){
                        $(".ekspedisi-detail .card").removeClass('ekspedisi-selected');
                        $(this).find('.card').addClass('ekspedisi-selected');
                        var value = $(this).find('.ekspedisi_value').val();
                        var values = JSON.parse(window.atob(value));
                        values.carrier_id = carrier_id;
                        self._rpc({route:'/shop/update_carrier', params: values})
                        .then(self._handleCarrierUpdateResult.bind(self));
                    });

                    $(".ekspedisi-detail").hover(function(){
                        $(this).find('.card').addClass('ekspedisi-hover');
                    },function(){
                        $(this).find('.card').removeClass('ekspedisi-hover');
                    });                 
                }
            },function(err){
                $.unblockUI();
                setErrorMessage(true, 'Terjadi kesalahan ! Coba lagi.');
            });
        }
    });

    var get_city = function(name){  
        if(name.length <= 2){
            return;
        }
        var self = this; 
        var values = {'name': name,'carrier_id': carrier_id}; 
        ajax.jsonRpc('/shop/get_city_list', 'call', values).
        then(function(result){
            $list_city_container.html('');
            if(result.length > 0){
                if(result[0].type == 'city'){
                    raja_ongkir_destination_type = 'city';
                    result[0].data.forEach(function(item){
                        var option = '<li class="list-group-item city-item"';
                        option += ' data-city-id="' + item['city_id'] + '"';
                        option += ' data-city-name="' + item['type'] + ' ' + item['name'] + ' (' + item['province']  + ')">';
                        option += item['type'] + ' ' + item['name'] + ' (' + item['province']  + ')</li>';
                        $list_city_container.append(option);
                    });
                }else{
                    raja_ongkir_destination_type = 'subdistrict';
                    result[0].data.forEach(function(item){
                        var option = '<li class="list-group-item city-item"';
                        option += ' data-city-id="' + item['subdistrict_id'] + '"';
                        option += ' data-city-name="' + item['name'] + ' ' + item['city_type'] + ' ' + item['city'] + ' (' + item['province']  + ')">';
                        option += item['name'] + ' ' + item['city_type'] + ' ' + item['city'] + ' (' + item['province']  + ')</li>';
                        $list_city_container.append(option);
                    });
                }
            }            

            $('.city-item').on('click', function(e){  
                          
                city = parseInt($(this).attr('data-city-id'));
                $select_city.val($(this).attr('data-city-name'));
                $select_city_id.val(city);
            });
        },function(err){
            // framework.unblockUI();
        });
    };


    var get_destination_type = function(name){
        ajax.jsonRpc('/shop/get_destination_type', 'call').
        then(function(result){
            raja_ongkir_destination_type = result;
        },function(err){
            // framework.unblockUI();
        });
    };

    $select_city.on('focus', function(){
        $list_city_container.removeClass('item-hidden');
    });

    $select_city.on('blur', function(){  
        
        setTimeout(function(){ 
            $list_city_container.addClass('item-hidden');
        }, 600);
    });

    $select_city.on('keyup', function(){
        var value = $(this).val();
        $select_city_id.val(null);
        get_city(value);
    });

    get_destination_type();

});
