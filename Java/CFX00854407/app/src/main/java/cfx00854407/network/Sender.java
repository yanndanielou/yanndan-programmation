/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package cfx00854407.network;


import java.io.IOException;
import java.net.SocketException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * Sender is responsible for sending data to the network. Once this object is
 * constructed the actual IP address and port number is remembered by this
 * object. When different IP address/port is required a new Sender must be
 * constructed.
 *
 * @author Z003URXB
 */
public class Sender  {
	private static final Logger LOGGER = LogManager.getLogger(Sender.class);

    //network values
    private final String ipAddress;
    private final int port;
    
    public static short bim_id = 0;

    public Sender() {
        this.ipAddress = cfx00854407.constants.Constants.AFFCAR_IP_ADDRESS;
        this.port = cfx00854407.constants.Constants.PAE_AFFCAR_DESTINATION_PORT;
    }


    public void sendPaeAffcarMessage(boolean displayed_color, short countdown_time_value) {
        //prepare time data
        CBTCPacket cbtcPacket = new CBTCPacket(new Message());
        cbtcPacket.setNo_Bim(bim_id++);
        if(cfx00854407.constants.Constants.ACK_REQUIRED) {
            cbtcPacket.setNo_Ar((byte)0x0f);        
        }
        //System.out.println("bim: "+bim_id);
        cbtcPacket.setId_Msg(cfx00854407.constants.Constants.PAE_AFFCAR_MESSAGE_ID);
        cbtcPacket.setSource_Address(cfx00854407.constants.Constants.PAE_CBTC_ADDRESS);
        cbtcPacket.setDestination_Address(cfx00854407.constants.Constants.AFFCAR_CBTC_ADDRESS);
        ((Message)cbtcPacket.getMessage()).setAffcarMode(cfx00854407.constants.Constants.AFFCAR_1_MODE, cfx00854407.constants.Constants.AFFCAR_2_MODE);
        ((Message)cbtcPacket.getMessage()).setDisplayColor(displayed_color);
        ((Message)cbtcPacket.getMessage()).setCountdownValue(countdown_time_value);
        //byte[] packetData = cbtcPacket.getBytes();

        
        //send packet
        try {
            cbtcPacket.sendPacket(ipAddress, port);
        } catch (SocketException ex) {
        	LOGGER.error(ex.getMessage());          
        } catch (IOException ex) {
        	LOGGER.error(ex.getMessage());
        } catch (PacketFormatException ex) {
        	LOGGER.error(ex.getMessage());
        }
    }


}
