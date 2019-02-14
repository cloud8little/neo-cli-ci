# -*- coding: utf-8 -*-
import sys
sys.path.append('..')


class test_config():
    nodecount=4
    ###wallet_5.json的另一个地址
    address_default = "AN1YFukQqC7PhEqnVhp7Au9Skh4shWdjJb"
    ###wallet_5.json内不存在的地址    
    address_notexist1 = "ALhZme2s6b7mcRuJgqwVkxSN5jNgm27Mku"
    address_wrong_str = "abc"    
    privkey = "L31rLw3AyK7PjMvioQHiVosbw64mvhwqhmPGZhhjbbxpdBDxXwEG"    
    asset_id_neo = "0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"
    asset_id_gas = "0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7"
    assetstate = {"name": [{"lang": "zh-CN","name": "\u5c0f\u8681\u80a1"},{"lang": "en","name": "AntShare"}],"owner": "00","issuer": "Abf2qMs1pzQb8kYk9RuxtUb9jtRKJVuBJt","id": "0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b","amount": "100000000","type": "GoverningToken","admin": "Abf2qMs1pzQb8kYk9RuxtUb9jtRKJVuBJt","precision": 0,"available": "100000000","expiration": 4000000,"frozen": False,"version": 0}
    asset_id_notexist = "025d82f7b00a9ff1cfe709abe3c4741a105d067178e645bc3ebad9bc79af47d4"
    asset_id_notexist_result = {"balance": "0"}
    asset_id_wrong_str = "abc"
    ###index为100的hash值
    hash_default = "0x56cc22c4dcdf24ea68c3c8a3d936d938667f6a19304a1d1b8ce4854eec9b3a9c"
    hash_notexist = "abcdd2dae4a9c9275290f89b56e67d7363ea4826dfd4fc13cc01cf73a44b0d0e"
    hash_wrong_str = "abc"    
    message_serialized = "0000000006aa325da6367e78f0a63772bff9352338f8539c97acd2aae4a4d4b2abded88f21cfa54b7c3511950880c7a23de3c1cd4d1ab0d7570dfc2ae02a7ceca650f676a76f245c640000004579bd9992892aa93bc2ef525ce3bbd911dee3bd3c5496bbdb2abea301c34070ed957c56866cd3ee1e377c01132b5d41858ecfd6af73260a7fb759503d08b130858a9314efc469c3a4df92ed0fd6c4f34c1e1ed2d34a51605a7e49dc2ac74d401bb687941c27cb66007714956553cc79be948d8bfaebf6c6a1201da3cc30ce4f0b98ec1cfcf5dd5d78838469a6f77ffd907fb088ad5d757e72a7251c40fb5e9f4047396c9bd2b522b1929c7a7a0089ed73b244e12b4d3fe7fe53ca33e1a3c262c5cc9093ac26982af9721b219c78385dad224f24fc7c740e983d3df862c3cd5d138b5321021e5f82f1dac5f8662280e1e710b3a10e9c792ebd21fe31557354edd620b5d1b821032bbbc3dd52542af02af57927862a63faeab58c78d18d072b9d754646c3a6575321034dea68befe59ff741c7b6a8641da7ecd78262f9f7e906e127f6600d1abc6142c2102f66163ebbd00bc435b2fab84ed4dc873fd2bbcddb74902ec6086bb9cc580063654ae0100004579bd9900000000"
    node_default = 5
    node_other1 = 1   
    node_other5 = 3   
    verbose_right = 0    
    verbose_negative = -2
    verbose_beyond = 10    
    verbose_wrong_str = "abc"
    index_right = 100
    index_right_zero = 0    
    index_wrong_str = "abc"
    index_negative = -10    
 
    blocksysfee_indexNonzero = "490"
    blocksysfee = "0"    
    message_serialized2 = "0000000006aa325da6367e78f0a63772bff9352338f8539c97acd2aae4a4d4b2abded88f21cfa54b7c3511950880c7a23de3c1cd4d1ab0d7570dfc2ae02a7ceca650f676a76f245c640000004579bd9992892aa93bc2ef525ce3bbd911dee3bd3c5496bbdb2abea301c34070ed957c56866cd3ee1e377c01132b5d41858ecfd6af73260a7fb759503d08b130858a9314efc469c3a4df92ed0fd6c4f34c1e1ed2d34a51605a7e49dc2ac74d401bb687941c27cb66007714956553cc79be948d8bfaebf6c6a1201da3cc30ce4f0b98ec1cfcf5dd5d78838469a6f77ffd907fb088ad5d757e72a7251c40fb5e9f4047396c9bd2b522b1929c7a7a0089ed73b244e12b4d3fe7fe53ca33e1a3c262c5cc9093ac26982af9721b219c78385dad224f24fc7c740e983d3df862c3cd5d138b5321021e5f82f1dac5f8662280e1e710b3a10e9c792ebd21fe31557354edd620b5d1b821032bbbc3dd52542af02af57927862a63faeab58c78d18d072b9d754646c3a6575321034dea68befe59ff741c7b6a8641da7ecd78262f9f7e906e127f6600d1abc6142c2102f66163ebbd00bc435b2fab84ed4dc873fd2bbcddb74902ec6086bb9cc580063654ae00"
    contractstate_message = {"author": "56","email": "78","code_version": "34","returntype": "ByteArray","properties": {"storage": True,"dynamic_invoke": False},"version": 0,"description": "90","script": "0119c56b6c766b00527ac46c766b51527ac4616168164e656f2e52756e74696d652e47657454726967676572009c6c766b54527ac46c766b54c364c90061611417cf616df70247e8ec5efc80c139450608f3536cc001149c6c766b55527ac46c766b55c364400061611417cf616df70247e8ec5efc80c139450608f3536c6168184e656f2e52756e74696d652e436865636b5769746e6573736c766b56527ac4620c03611417cf616df70247e8ec5efc80c139450608f3536cc001219c6c766b57527ac46c766b57c3643600616c766b00c36c766b58527ac46c766b58c3611417cf616df70247e8ec5efc80c139450608f3536cac6c766b56527ac462b002616233026168164e656f2e52756e74696d652e47657454726967676572609c6c766b59527ac46c766b59c3640902616c766b00c3066465706c6f79876c766b5a527ac46c766b5ac3641100616592026c766b56527ac46257026c766b00c30a6d696e74546f6b656e73876c766b5b527ac46c766b5bc36411006165ae036c766b56527ac46229026c766b00c30b746f74616c537570706c79876c766b5c527ac46c766b5cc364110061658f056c766b56527ac462fa016c766b00c3046e616d65876c766b5d527ac46c766b5dc36411006165e5016c766b56527ac462d2016c766b00c30673796d626f6c876c766b5e527ac46c766b5ec36411006165cb016c766b56527ac462a8016c766b00c3087472616e73666572876c766b5f527ac46c766b5fc3647700616c766b51c3c0539c009c6c766b0113527ac46c766b0113c3640e00006c766b56527ac46263016c766b51c300c36c766b60527ac46c766b51c351c36c766b0111527ac46c766b51c352c36c766b0112527ac46c766b60c36c766b0111c36c766b0112c361527265fa046c766b56527ac46216016c766b00c30962616c616e63654f66876c766b0114527ac46c766b0114c3644d00616c766b51c3c0519c009c6c766b0116527ac46c766b0116c3640e00006c766b56527ac462ce006c766b51c300c36c766b0115527ac46c766b0115c36165a7066c766b56527ac462ab006c766b00c308646563696d616c73876c766b0117527ac46c766b0117c36411006165b0006c766b56527ac4627d006161659d086c766b52527ac46165120a6c766b53527ac46c766b53c300907c907ca1630e006c766b52c3c000a0620400006c766b0118527ac46c766b0118c364300061616c766b52c36c766b53c3617c06726566756e6453c168124e656f2e52756e74696d652e4e6f746966796161006c766b56527ac46203006c766b56c3616c756600c56b086e65703574657374616c756600c56b086e65703574657374616c756600c56b58616c756653c56b616168164e656f2e53746f726167652e476574436f6e746578740b746f74616c537570706c79617c680f4e656f2e53746f726167652e4765746c766b00527ac46c766b00c3c000a06c766b51527ac46c766b51c3640e00006c766b52527ac462df006168164e656f2e53746f726167652e476574436f6e74657874611417cf616df70247e8ec5efc80c139450608f3536c070000c16ff28623615272680f4e656f2e53746f726167652e507574616168164e656f2e53746f726167652e476574436f6e746578740b746f74616c537570706c79070000c16ff28623615272680f4e656f2e53746f726167652e507574616100611417cf616df70247e8ec5efc80c139450608f3536c070000c16ff28623615272087472616e7366657254c168124e656f2e52756e74696d652e4e6f7469667961516c766b52527ac46203006c766b52c3616c75665ac56b616165a5066c766b00527ac46c766b00c3c0009c6c766b56527ac46c766b56c3640f0061006c766b57527ac462d8016165f7076c766b51527ac4616588046c766b52527ac46c766b52c3009c6c766b58527ac46c766b58c3643a0061616c766b00c36c766b51c3617c06726566756e6453c168124e656f2e52756e74696d652e4e6f7469667961006c766b57527ac46275016c766b00c36c766b51c36c766b52c361527265b4046c766b53527ac46c766b53c3009c6c766b59527ac46c766b59c3640f0061006c766b57527ac46237016168164e656f2e53746f726167652e476574436f6e746578746c766b00c3617c680f4e656f2e53746f726167652e4765746c766b54527ac46168164e656f2e53746f726167652e476574436f6e746578746c766b00c36c766b53c36c766b54c393615272680f4e656f2e53746f726167652e507574616168164e656f2e53746f726167652e476574436f6e746578740b746f74616c537570706c79617c680f4e656f2e53746f726167652e4765746c766b55527ac46168164e656f2e53746f726167652e476574436f6e746578740b746f74616c537570706c796c766b53c36c766b55c393615272680f4e656f2e53746f726167652e5075746161006c766b00c36c766b53c3615272087472616e7366657254c168124e656f2e52756e74696d652e4e6f7469667961516c766b57527ac46203006c766b57c3616c756651c56b616168164e656f2e53746f726167652e476574436f6e746578740b746f74616c537570706c79617c680f4e656f2e53746f726167652e4765746c766b00527ac46203006c766b00c3616c75665bc56b6c766b00527ac46c766b51527ac46c766b52527ac4616c766b52c300a16c766b55527ac46c766b55c3640e00006c766b56527ac462d8016c766b00c36168184e656f2e52756e74696d652e436865636b5769746e657373009c6c766b57527ac46c766b57c3640e00006c766b56527ac4629c016c766b51c3c001149c009c6c766b58527ac46c766b58c3640e00006c766b56527ac46277016168164e656f2e53746f726167652e476574436f6e746578746c766b00c3617c680f4e656f2e53746f726167652e4765746c766b53527ac46c766b53c36c766b52c39f6c766b59527ac46c766b59c3640e00006c766b56527ac4621a016c766b00c36c766b51c39c6c766b5a527ac46c766b5ac3640e00516c766b56527ac462f5006168164e656f2e53746f726167652e476574436f6e746578746c766b00c36c766b53c36c766b52c394615272680f4e656f2e53746f726167652e507574616168164e656f2e53746f726167652e476574436f6e746578746c766b51c3617c680f4e656f2e53746f726167652e4765746c766b54527ac46168164e656f2e53746f726167652e476574436f6e746578746c766b51c36c766b54c36c766b52c393615272680f4e656f2e53746f726167652e50757461616c766b00c36c766b51c36c766b52c3615272087472616e7366657254c168124e656f2e52756e74696d652e4e6f7469667961516c766b56527ac46203006c766b56c3616c756652c56b6c766b00527ac4616168164e656f2e53746f726167652e476574436f6e746578746c766b00c3617c680f4e656f2e53746f726167652e4765746c766b51527ac46203006c766b51c3616c756655c56b616168134e656f2e52756e74696d652e47657454696d656c766b00527ac46c766b00c30480bfcf59946c766b51527ac46c766b51c3009f6c766b52527ac46c766b52c3640f0061006c766b53527ac4623a006c766b51c3048033e1019f6c766b54527ac46c766b54c3641400610500e87648176c766b53527ac4620f0061006c766b53527ac46203006c766b53c3616c756659c56b6c766b00527ac46c766b51527ac46c766b52527ac4616c766b51c30400e1f505966c766b52c3956c766b53527ac46168164e656f2e53746f726167652e476574436f6e746578740b746f74616c537570706c79617c680f4e656f2e53746f726167652e4765746c766b54527ac4070000c16ff286236c766b54c3946c766b55527ac46c766b55c300a16c766b56527ac46c766b56c3643a0061616c766b00c36c766b51c3617c06726566756e6453c168124e656f2e52756e74696d652e4e6f7469667961006c766b57527ac46277006c766b55c36c766b53c39f6c766b58527ac46c766b58c3644e0061616c766b00c36c766b53c36c766b55c3946c766b52c3960400e1f50595617c06726566756e6453c168124e656f2e52756e74696d652e4e6f74696679616c766b55c36c766b53527ac4616c766b53c36c766b57527ac46203006c766b57c3616c756657c56b6161682953797374656d2e457865637574696f6e456e67696e652e476574536372697074436f6e7461696e65726c766b00527ac46c766b00c361681d4e656f2e5472616e73616374696f6e2e4765745265666572656e6365736c766b51527ac4616c766b51c36c766b52527ac4006c766b53527ac4629e006c766b52c36c766b53c3c36c766b54527ac4616c766b54c36168154e656f2e4f75747075742e4765744173736574496461209b7cffdaa674beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc59c6c766b55527ac46c766b55c3642d006c766b54c36168184e656f2e4f75747075742e476574536372697074486173686c766b56527ac4622c00616c766b53c351936c766b53527ac46c766b53c36c766b52c3c09f6359ff006c766b56527ac46203006c766b56c3616c756651c56b6161682d53797374656d2e457865637574696f6e456e67696e652e476574457865637574696e67536372697074486173686c766b00527ac46203006c766b00c3616c756658c56b6161682953797374656d2e457865637574696f6e456e67696e652e476574536372697074436f6e7461696e65726c766b00527ac46c766b00c361681a4e656f2e5472616e73616374696f6e2e4765744f7574707574736c766b51527ac4006c766b52527ac4616c766b51c36c766b53527ac4006c766b54527ac462ce006c766b53c36c766b54c3c36c766b55527ac4616c766b55c36168184e656f2e4f75747075742e47657453637269707448617368616505ff907c907c9e6346006c766b55c36168154e656f2e4f75747075742e4765744173736574496461209b7cffdaa674beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc59c620400006c766b56527ac46c766b56c3642d00616c766b52c36c766b55c36168134e656f2e4f75747075742e47657456616c7565936c766b52527ac461616c766b54c351936c766b54527ac46c766b54c36c766b53c3c09f6329ff6c766b52c36c766b57527ac46203006c766b57c3616c7566","hash": "0xe09da9b65a732bd57ca0c34f101ff11d14670522","parameters":["String","Array"],"name": "12"}
    contract_script_hash = "0xe09da9b65a732bd57ca0c34f101ff11d14670522"
    contract_script_hash_notexist = "0xe09da9b65a732bd57ca0c34f101ff11d146791a6"
    contract_script_hash_wrong_str = "abc"    
    key = "6e616d65"
    key_wrong_str = "616263"
    storage_value = "6e65703574657374"
    ###index为100的txid值
    txid = "0x76f650a6ec7c2ae02afc0d57d7b01a4dcdc1e33da2c780089511357c4ba5cf21"
    txid_wrong_notexist = "0x12774806b2f59970cd7b08c02f6db7694583a2dbaaa6d3d851459aedea472abc"
    txid_wrong_str = "abc"
    txid_wrong_int = 123
    message_serialized3 = "00004579bd9900000000"  
    port = 50001  
    script_notexist="00046e616d65675f0e5a86edd8e1f62b68d2b3f7c0a761fc5a67dc"
    
    invokescript="00c1046e616d6567220567141df11f104fc3a07cd52b735ab6a99de0"
    invokescript_notexist="00046e616d656724058e5e1b6008847cd662728549088a9ee8219e"
    invokescript_wrong_str="abcd"
    tx="d1011b00046e616d6567220567141df11f104fc3a07cd52b735ab6a99de0000000000000000000000000"
    address_notexist="AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz"
    hex_right="800000019c7537ede87b3ea7b8ae38492c1e224885dd6f2ff88e2b6e959156f63c202f980100029b7cffdaa674beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc500e1f50500000000a55d4cae8feb37874f9ffe9a5d7062228b5efe4c9b7cffdaa674beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc5007ce957f286230017cf616df70247e8ec5efc80c139450608f3536c014140ecc2572ba96a1ad4010d737823e1a53dfe299fa09714b129b11628885e6d313d27cd9277317168399e615cfbae9eb165e7c743198f10d2015658caeab1e1e935232103ae5dddd3101c2a300f7066dc62df4bd5893036223fd0e4ef6569f19ccb6d8fabac"
    hex_notexists="800000019c7537ede87b3ea7b8ae38492c1e224885dd6f2ff88e2b6e959156f63c202f980100029b7cffdaa674beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc500e1f50500000000a55d4cae8feb37874f9ffe9a5d7062228b5efe4c9b7cffdaa674beae0f930ebe6085af9093e5fe56b34a5c220ccdcf6efc336fc5007ce957f286230017cf616df70247e8ec5efc80c139450608f3536c014140ecc2572ba96a1ad4010d737823e1a53dfe299fa09714b129b11628885e6d313d27cd9277317168399e615cfbae9eb165e7c743198f10d2015658caeab1e1e935232103ae5dddd3101c2a300f7066dc62df4bd5893036223fd0e4ef6569f19ccb6d9fabac"    
    wrong_str = "abc"
    wrong_int = 123
    script="00046e616d6567220567141df11f104fc3a07cd52b735ab6a99de0"
    pass
