<?php
# for now we skip login.php
session_name('aamks');
require_once("inc.php"); 

if(empty($_SESSION['nn'])) { $_SESSION['nn']=new Aamks("Aamks") ; } 
init_main_vars();
$_SESSION['main']['scenario_name']=$_GET['s'];
$_SESSION['main']['scenario_id']=NULL;
$_SESSION['main']['project_name']=$_GET['p'];
$_SESSION['main']['working_home']="/home/aamks_users/mimoohowy@gmail.com/demo/$_GET[s]";
$_SESSION['main']['user_id']=1;
$r=$_SESSION['nn']->query("SELECT preferences FROM users WHERE id=$1", array($_SESSION['main']['user_id']));
$_SESSION['prefs']=json_decode($r['preferences'],1);

if(isset($_GET['apainter'])) { 
	header("Location: /aamks/apainter/index.php"); 
} else {
	header("Location: /aamks/animator/index.php"); 
}

?>
