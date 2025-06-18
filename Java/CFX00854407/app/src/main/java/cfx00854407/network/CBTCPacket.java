/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package cfx00854407.network;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetSocketAddress;
import java.net.SocketException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 *
 * @author Z003URXB
 */
public class CBTCPacket {
	private static final Logger LOGGER = LogManager.getLogger(CBTCPacket.class);

    public static final int HEADER_SIZE = 9;
    public static final int ID_ACK = 189;

    public short No_Bim;
    public byte No_Ar;
    public byte Id_Msg;
    public short Source_Address;
    public short Destination_Address;

    private byte[] bytes;

    private AFFCARMessage message;
    
    public CBTCPacket() {
    }

    public CBTCPacket(AFFCARMessage message) {
        this.message = message;
    }

    public AFFCARMessage getMessage() {
        return message;
    }

    public byte[] getBytes() throws PacketFormatException {
        byte[] packetData = new byte[17];
        packetData[0] = (byte) (0xff & (No_Bim>>8));
        packetData[1] = (byte) (0xff & No_Bim);
        packetData[2] = No_Ar;
        packetData[3] = 0;//empty byte
        packetData[4] = Id_Msg;
        packetData[5] = (byte) (0xff & (Source_Address>>8));
        packetData[6] = (byte) (0xff & Source_Address);
        packetData[7] = (byte) (0xff & (Destination_Address>>8));
        packetData[8] = (byte) (0xff & Destination_Address);
        
        
        
        byte[] msgData = message.getBytes();
        System.arraycopy(msgData, 0, packetData, HEADER_SIZE, msgData.length);

        return packetData;
    }

    public void putBytes(byte[] bytes) {
        if (bytes.length > HEADER_SIZE) {
            this.bytes = bytes;

            //cbtc header
            this.No_Bim = (short) (((0xff & bytes[0]) << 8) | (0xff & bytes[1]));
            this.No_Ar = bytes[2];
            this.Id_Msg = bytes[4];
            this.Source_Address = (short) (((0xff & bytes[5]) << 8) | (0xff & bytes[6]));
            this.Destination_Address = (short) (((0xff & bytes[7]) << 8) | (0xff & bytes[8]));

            //message
            if ((0xff&Id_Msg) == cfx00854407.constants.Constants.AFFCAR_PAE_MESSAGE_ID) { //message to AFFCAR
                this.message = new Message();
                byte[] b = new byte[Message.MSG_SIZE];
                System.arraycopy(bytes, HEADER_SIZE, b, 0, b.length);
                this.message.putBytes(b);
            }
            else if ((0xff&Id_Msg) == cfx00854407.constants.Constants.PAE_AFFCAR_MESSAGE_ID) { //message from AFFCAR
                this.message = new Response();
                byte[] b = new byte[Response.MSG_SIZE];
                System.arraycopy(bytes, HEADER_SIZE, b, 0, b.length);
                this.message.putBytes(b);
            }
            else if ((0xff&Id_Msg) == ID_ACK) { //acknowledgement from AFFCAR
                this.message = new Acknowledgement();
                byte[] b = new byte[Acknowledgement.MSG_SIZE];
                System.arraycopy(bytes, HEADER_SIZE, b, 0, b.length);
                this.message.putBytes(b);
            }
        }
    }

    public void sendPacket(String ipAddr, int port) throws SocketException, IOException, PacketFormatException {
        //send udp datagram
        DatagramSocket udpSocket = null;
        bytes = getBytes();
        DatagramPacket packet = new DatagramPacket(bytes, bytes.length);

        LOGGER.info(()->"sendPacket packet:"+packet+ ", bytes:" + bytes);
        
        udpSocket = new DatagramSocket();
        packet.setSocketAddress(new InetSocketAddress(ipAddr, port));
        udpSocket.send(packet);

    }

    public short getNo_Bim() {
        return No_Bim;
    }

    public void setNo_Bim(short No_Bim) {
        this.No_Bim = No_Bim;
    }

    public byte getNo_Ar() {
        return No_Ar;
    }

    public void setNo_Ar(byte No_Ar) {
        this.No_Ar = No_Ar;
    }

    public byte getId_Msg() {
        return Id_Msg;
    }

    public void setId_Msg(byte Id_Msg) {
        this.Id_Msg = Id_Msg;
    }

    public short getSource_Address() {
        return Source_Address;
    }

    public void setSource_Address(int Source_Address) {
        this.Source_Address = (short)Source_Address;
    }

    public short getDestination_Address() {
        return Destination_Address;
    }

    public void setDestination_Address(int Destination_Address) {
        this.Destination_Address = (short)Destination_Address;
    }
}
