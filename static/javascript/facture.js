function Calculate(){  
  var len = $('table.table tbody tr').length;
  var $tot = 0;
  var $tot_tva = 0;
  for(var i=0; i<len ; i++){
    var $qte = $('table.table tbody tr:eq('+i+') td:eq(1) span').html(); 
    var $puht = $('table.table tbody tr:eq('+i+') td:eq(2) span').html();
    var $tot_ht = $qte*$puht;
    /* remplit la case total HT par qte*prix unitaire HT */
    $('table.table tbody tr:eq('+i+') td:eq(3)').html($tot_ht.toFixed(2)+' €');
    $tot +=  $tot_ht;
    var $tva = $('table.table tbody tr:eq('+i+') td:eq(4) span').html().replace(',','.');
    $tot_tva += ($tva*$tot_ht)/100;
  }
  
  $('table.total tbody tr td:eq(0)').html($tot_tva.toFixed(2)+' €'); 
  $('table.total tbody tr td:eq(1)').html($tot.toFixed(2)+' €');
  var $tot_ttc = $tot_tva + $tot;
  $('table.total tbody tr td:eq(2)').html($tot_ttc.toFixed(2)+' €'); 
}

function AddLine(){
  $('table.table tbody').append('<tr><td><div class="first last"><div contenteditable="true" class="" title=""></div></div></td><td><span contenteditable="true">1</span></td><td><span contenteditable="true">0</span>&nbsp;€</td><td>&nbsp;</td><td><span contenteditable="true">19,6</span>&nbsp;%</td></tr>');
}

function RemLine(){
  $('table.table:eq(0) tbody tr:last').remove();
  Calculate();
}

$(function () {
    $("table.table").on('blur', "span[contenteditable=true]", function () { Calculate() });
});

