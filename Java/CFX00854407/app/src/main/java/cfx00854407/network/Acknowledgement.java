/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package cfx00854407.network;

/**
 *
 * @author z003urxb
 */
public class Acknowledgement implements AFFCARMessage{

    public static final int MSG_SIZE = 1;
    
    private byte No_Ar_Acq = (byte)0x00;
    
    public Acknowledgement() {
    }
    
    @Override
    public byte[] getBytes() throws PacketFormatException {
        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public void putBytes(byte[] bytes) {
        if(bytes.length>=MSG_SIZE){
            No_Ar_Acq = bytes[0];
        }
    }

    public byte getNo_Ar_Acq() {
        return No_Ar_Acq;
    }

    public void setNo_Ar_Acq(byte No_Ar_Acq) {
        this.No_Ar_Acq = No_Ar_Acq;
    }
    
}
