function Calculate(){  
  var len = $('table.docutils:eq(0) tbody tr').length;
  var $tot = 0;
  var $tot_tva = 0;
  for(var i=0; i<len ; i++){
    var $qte = $('table.docutils:eq(0) tbody tr:eq('+i+') td:eq(1) span').html(); 
    var $puht = $('table.docutils:eq(0) tbody tr:eq('+i+') td:eq(2) span').html();
    var $tot_ht = $qte*$puht;
    /* remplit la case total HT par qte*prix unitaire HT */
    $('table.docutils:eq(0) tbody tr:eq('+i+') td:eq(3)').html($tot_ht.toFixed(2)+' €');
    $tot +=  $tot_ht;
    var $tva = $('table.docutils:eq(0) tbody tr:eq('+i+') td:eq(4) span').html().replace(',','.');
    $tot_tva += ($tva*$tot_ht)/100;
  }
  
  $('table.docutils:eq(1) tbody tr td:eq(0)').html($tot_tva.toFixed(2)+' €'); 
  $('table.docutils:eq(1) tbody tr td:eq(1)').html($tot.toFixed(2)+' €');
  var $tot_ttc = $tot_tva + $tot;
  $('table.docutils:eq(1) tbody tr td:eq(2)').html($tot_ttc.toFixed(2)+' €'); 
}

function AddLine(){
  $('table.docutils:eq(0) tbody').append('<tr><td><div class="first last"><div contenteditable="true" title=""></div></div></td><td><div class="first last"><div contenteditable="true" title=""></div></div></td><td><span contenteditable="true">0</span>&nbsp;€</td><td>&nbsp;</td><td><span contenteditable="true">19,6</span>&nbsp;%</td></tr>');
}

function RemLine(){
  $('table.docutils:eq(0) tbody tr:last').remove();
  Calculate();
}


     $('table.docutils:eq(0) tbody tr:eq(0) td:eq(1) span, table.docutils:eq(0) tbody tr:eq(0) td:eq(2) span, table.docutils:eq(0) tbody tr:eq(0) td:eq(4) span').change(alert('qpuc')  );
